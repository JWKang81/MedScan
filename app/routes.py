import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Prescription
import uuid
# 匯入你剛寫好的兩個核心辨識函數
from .recognition import scan_prescription, parse_da_pharmacy

main_bp = Blueprint('main', __name__)

# 允許的檔案格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
from flask import render_template_string # 用來直接渲染字串或讀取檔案

@main_bp.route('/')
def index():
    # 這裡假設你的 index.html 放在專案根目錄
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())


@main_bp.route('/api/upload', methods=['POST'])
def upload_prescription():
    """
    上傳藥袋影像並進行 OCR 辨識
    ---
    tags:
      - Prescription Processing
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 藥袋的照片 (支援 jpg, png)
    responses:
      201:
        description: 上傳並辨識成功，回傳萃取出的資料
      400:
        description: 檔案格式錯誤或未上傳檔案
      500:
        description: OCR 辨識過程發生系統錯誤
    """
    # 1. 基本檔案檢查
    if 'file' not in request.files:
        return jsonify({"error": "請上傳圖片檔案"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未選取檔案"}), 400

    if file and allowed_file(file.filename):
        # 2. 儲存檔案
        filename = f"{uuid.uuid4().hex}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 3. 在資料庫建立一筆紀錄 (狀態暫定為 processing)
        new_pre = Prescription(
            user_id=1,  # 目前先預設為 id=1 的使用者
            image_path=filename,
            status='processing'
        )
        db.session.add(new_pre)
        db.session.commit()

        # 4. 啟動辨識流程 (串接 recognition.py)
        # 第一步：獲取原始文字 (OCR)
        raw_text = scan_prescription(file_path)
        
        # 第二步：利用正則表達式擷取關鍵資訊 (Regex)
        # 注意：如果 OCR 失敗，raw_text 會是錯誤訊息字串
        if "辨識過程發生錯誤" in raw_text:
            return jsonify({
                "error": "OCR 辨識失敗",
                "details": raw_text
            }), 500
            
        extracted_data = parse_da_pharmacy(raw_text)

        # 5. 回傳結果給前端，讓使用者確認或修改
        return jsonify({
            "message": "上傳並辨識成功",
            "prescription_id": new_pre.id,
            "data": extracted_data,
            "raw_debug": raw_text[:200]  # 回傳前 200 字供除錯
        }), 201

    return jsonify({"error": "不支援的檔案格式"}), 400

@main_bp.route('/api/confirm', methods=['POST'])
def confirm_prescription():
    """
    接收前端修改後的最終資料，並正式寫入資料庫
    ---
    tags:
      - Prescription Processing
    parameters:
      - in: body
        name: body
        required: true
        description: 包含藥單ID與使用者校正後的各項明細
        schema:
          type: object
          properties:
            prescription_id:
              type: integer
              example: 1
            data:
              type: object
              properties:
                patient_name:
                  type: string
                  example: "王小明"
                medicine_ch_name:
                  type: string
                  example: "紐黴素糖衣錠"
    responses:
      200:
        description: 資料已成功存入系統
      400:
        description: 缺少資料或格式錯誤
      404:
        description: 找不到該筆藥單紀錄
      500:
        description: 存檔或資料庫寫入失敗
    """
    data = request.json
    if not data:
        return jsonify({"error": "缺少資料"}), 400

    # 取得前端傳回的資訊
    prescription_id = data.get('prescription_id')
    final_data = data.get('data') # 這裡包含使用者修正後的姓名、藥名、天數等

    if not prescription_id or not final_data:
        return jsonify({"error": "資料格式不正確"}), 400

    try:
        # 1. 更新主表 Prescription 的資訊與狀態
        prescription = Prescription.query.get(prescription_id)
        if not prescription:
            return jsonify({"error": "找不到該筆藥單紀錄"}), 404

        prescription.hospital_name = final_data.get('hospital')
        prescription.patient_name = final_data.get('patient_name')
        prescription.status = 'completed' # 標記為處理完成
        
        # 處理日期格式 (從 YYYY/MM/DD 轉為 date 物件，若格式不合則跳過)
        from datetime import datetime
        raw_date = final_data.get('dispensing_date')
        if raw_date:
            try:
                prescription.dispense_date = datetime.strptime(raw_date, '%Y/%m/%d')
            except ValueError:
                pass

        # 2. 寫入藥品明細表 Medication
        from app.models import Medication
        
        # 先檢查是否已經有藥品明細，若有則先刪除（防止重複提交）
        Medication.query.filter_by(prescription_id=prescription_id).delete()

        # 建立新的藥品紀錄
        new_med = Medication(
            prescription_id=prescription_id,
            medicine_name=final_data.get('medicine_ch_name'),
            dosage="每次 1 粒", # 這部分未來可以從 Regex 進一步細分
            frequency=final_data.get('usage_instruction'),
            days=int(final_data.get('days') or 0),
            indications=final_data.get('indications'),
            side_effects=final_data.get('side_effects')
        )
        
        db.session.add(new_med)
        db.session.commit()

        return jsonify({
            "message": "資料已成功存入系統",
            "status": "success"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"存檔失敗: {str(e)}"}), 500

@main_bp.route('/test', methods=['GET'])
def test_connection():
    """
    測試後端伺服器是否正常運作
    ---
    tags:
      - System Info
    responses:
      200:
        description: 伺服器運作正常
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: Flask 後端已啟動
    """
    return jsonify({
        "status": "success",
        "message": "Flask 後端已啟動，資料庫連線正常！"
    }), 200