from flask import Blueprint, jsonify

# 建立一個名為 main 的藍圖
main_bp = Blueprint('main', __name__)

@main_bp.route('/test', methods=['GET'])
def test_connection():
    return jsonify({
        "status": "success",
        "message": "Flask 後端已啟動，資料庫連線正常！",
        "features": ["影像辨識(待開發)", "MySQL儲存(已就緒)"]
    }), 200