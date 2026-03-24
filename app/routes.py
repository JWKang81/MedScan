import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, render_template_string
from werkzeug.utils import secure_filename
from app import db
from app.models import Prescription, Medication
import uuid

# 匯入辨識函數
from .recognition import scan_prescription, parse_da_pharmacy

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# 系統與前端路由
# ==========================================

@main_bp.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

@main_bp.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"status": "success", "message": "Flask 後端已啟動！"}), 200


# ==========================================
# RESTful CRUD 路由 (針對 Resource: prescriptions)
# ==========================================

# 1. CREATE (新增/上傳並辨識藥袋)
@main_bp.route('/api/prescriptions', methods=['POST'])
def create_prescription():
    """上傳藥袋影像並進行 OCR 辨識 """
    if 'file' not in request.files:
        return jsonify({"error": "請上傳圖片檔案"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未選取檔案"}), 400

    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4().hex}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 建立資源
        new_pre = Prescription(user_id=1, image_path=filename, status='processing')
        db.session.add(new_pre)
        db.session.commit()

        # 啟動辨識
        raw_text = scan_prescription(file_path)
        if "辨識過程發生錯誤" in raw_text:
            return jsonify({"error": "OCR 辨識失敗", "details": raw_text}), 500
            
        extracted_data = parse_da_pharmacy(raw_text)

        return jsonify({
            "message": "資源建立並辨識成功",
            "prescription_id": new_pre.id,
            "data": extracted_data,
            "raw_debug": raw_text[:200]
        }), 201 # 201 Created

    return jsonify({"error": "不支援的檔案格式"}), 400


# 2. READ ALL (取得所有藥單列表)
@main_bp.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    """取得所有藥單資料 (新增的實用功能)"""
    prescriptions = Prescription.query.all()
    result = []
    for p in prescriptions:
        result.append({
            "id": p.id,
            "patient_name": p.patient_name,
            "status": p.status,
            "image_path": p.image_path
        })
    return jsonify({"data": result}), 200


# 3. READ ONE (取得單一藥單詳細資訊)
@main_bp.route('/api/prescriptions/<int:pre_id>', methods=['GET'])
def get_prescription(pre_id):
    """取得特定 ID 的藥單明細"""
    prescription = Prescription.query.get(pre_id)
    if not prescription:
        return jsonify({"error": "找不到該筆紀錄"}), 404
    
    # 這裡可以連同 Medication 一起撈出來，省略實作細節
    return jsonify({
        "id": prescription.id,
        "patient_name": prescription.patient_name,
        "status": prescription.status
    }), 200


# 4. UPDATE (更新/確認藥單資料)
@main_bp.route('/api/prescriptions/<int:pre_id>', methods=['PUT'])
def update_prescription(pre_id):
    """接收修改後的最終資料，更新資料庫 (取代原本的 /confirm)"""
    data = request.json
    if not data or 'data' not in data:
        return jsonify({"error": "缺少資料"}), 400

    final_data = data.get('data')

    try:
        # 尋找指定資源
        prescription = Prescription.query.get(pre_id)
        if not prescription:
            return jsonify({"error": "找不到該筆紀錄"}), 404

        # 更新主表
        prescription.hospital_name = final_data.get('hospital')
        prescription.patient_name = final_data.get('patient_name')
        prescription.status = 'completed'
        
        raw_date = final_data.get('dispensing_date')
        if raw_date:
            try:
                prescription.dispense_date = datetime.strptime(raw_date, '%Y/%m/%d')
            except ValueError:
                pass

        # 更新明細表 (先刪後增)
        Medication.query.filter_by(prescription_id=pre_id).delete()
        new_med = Medication(
            prescription_id=pre_id,
            medicine_name=final_data.get('medicine_ch_name'),
            dosage="每次 1 粒",
            frequency=final_data.get('usage_instruction'),
            days=int(final_data.get('days') or 0),
            indications=final_data.get('indications'),
            side_effects=final_data.get('side_effects')
        )
        
        db.session.add(new_med)
        db.session.commit()

        return jsonify({"message": "資料已成功更新", "status": "success"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500


# 5. DELETE (刪除藥單)
@main_bp.route('/api/prescriptions/<int:pre_id>', methods=['DELETE'])
def delete_prescription(pre_id):
    """刪除指定藥單與其關聯的圖片、藥品明細"""
    try:
        prescription = Prescription.query.get(pre_id)
        if not prescription:
            return jsonify({"error": "找不到該筆紀錄"}), 404
        
        # 刪除關聯的 Medication (如果你在 model 裡有設 cascade='all, delete' 就不需要這行)
        Medication.query.filter_by(prescription_id=pre_id).delete()
        
        # 刪除 Prescription 主表
        db.session.delete(prescription)
        db.session.commit()
        
        # 可選：刪除實體圖片檔案
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], prescription.image_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({"message": "紀錄已刪除", "status": "success"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"刪除失敗: {str(e)}"}), 500
    
