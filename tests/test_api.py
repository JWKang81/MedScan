import pytest
from app import create_app
from app import db

# 這是 pytest 的 Fixture，用來在每個測試執行前準備好「乾淨的假環境」
@pytest.fixture
def client():
    # 1. 建立測試用的 Flask APP
    app = create_app()
    app.config['TESTING'] = True
    
    # 測試時切換到記憶體資料庫，確保測試速度極快且不影響正式 DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            # 2. 建立乾淨的資料表
            db.create_all()
            
        # 3. 將這個假的 client 交給測試函數使用
        yield client
        
        # 4. 測試結束後清理環境 (雖然記憶體 DB 關閉就消失了)
        with app.app_context():
            db.session.remove()
            db.drop_all()

# ==========================================
# 開始寫測試案例 (Test Cases)
# ==========================================

def test_system_status(client):
    """測試案例 1：確保系統測試 API 能正常回應 200"""
    # 模擬前端發送 GET 請求到 /test
    response = client.get('/test')
    
    # 斷言 (Assert)：我們「期望」得到的結果
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'Flask 後端已啟動' in response.json['message']

def test_upload_without_file(client):
    """測試案例 2：防呆機制測試，沒夾帶檔案應該被擋下並回傳 400"""
    # 模擬前端發送 POST 請求，但不帶任何檔案
    response = client.post('/api/upload')
    
    assert response.status_code == 400
    assert response.json['error'] == '請上傳圖片檔案'