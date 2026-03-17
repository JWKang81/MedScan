import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Prescription
import uuid

main_bp = Blueprint('main', __name__)

# 允許的檔案格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/api/upload', methods=['POST'])
def upload_prescription():
    # 1. 檢查是否有檔案傳入
    if 'file' not in request.files:
        return jsonify({"error": "沒有上傳檔案"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "未選取檔案"}), 400

    if file and allowed_file(file.filename):
        # 2. 確保檔名安全，並使用 UUID 重新命名防止重複
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        # 3. 儲存檔案到實體路徑
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        try:
            # 4. 寫入資料庫 (這裡暫時預設 user_id=1，之後做登入系統再調整)
            new_prescription = Prescription(
                user_id=1, 
                image_path=unique_filename,
                status='processing' # 標記為辨識中
            )
            db.session.add(new_prescription)
            db.session.commit()

            return jsonify({
                "message": "圖片上傳成功",
                "prescription_id": new_prescription.id,
                "image_url": unique_filename
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "檔案格式不支援 (僅限 jpg, png)"}), 400

@main_bp.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"status": "success", "message": "API 運作中"})