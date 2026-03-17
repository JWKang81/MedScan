import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Prescription
import uuid
# 匯入你剛寫好的兩個核心辨識函數
from .recognition import scan_prescription, parse_tzu_chi_prescription

main_bp = Blueprint('main', __name__)

# 允許的檔案格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/api/upload', methods=['POST'])
def upload_prescription():
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
            
        extracted_data = parse_tzu_chi_prescription(raw_text)

        # 5. 回傳結果給前端，讓使用者確認或修改
        return jsonify({
            "message": "上傳並辨識成功",
            "prescription_id": new_pre.id,
            "data": extracted_data,
            "raw_debug": raw_text[:200]  # 回傳前 200 字供除錯
        }), 201

    return jsonify({"error": "不支援的檔案格式"}), 400

@main_bp.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "running"})