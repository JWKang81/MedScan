import pytest
import io
import json
from unittest.mock import patch
from app import create_app, db

# ==========================================
# 1. 測試環境建置 (Fixtures)
# ==========================================

@pytest.fixture
def client():
    """建立測試用的 Flask 應用程式與記憶體資料庫"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # 測試專用記憶體資料庫
    # 確保測試時有設定 JWT 密鑰
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        # 測試結束後清理
        with app.app_context():
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """
    這是一把萬能鑰匙！
    它會自動幫測試腳本註冊、登入，並回傳帶有 JWT Token 的 HTTP Headers。
    """
    # 1. 先註冊一個測試帳號
    client.post('/api/auth/register', json={
        "username": "test_dev",
        "password": "secure_password",
        "email": "dev@test.com"
    })
    
    # 2. 登入取得 Token
    response = client.post('/api/auth/login', json={
        "username": "test_dev",
        "password": "secure_password"
    })
    token = response.get_json()['access_token']
    
    # 3. 組裝成標準的 Authorization 標頭格式
    return {
        'Authorization': f'Bearer {token}'
    }


# ==========================================
# 2. 認證系統測試 (Auth Tests)
# ==========================================

def test_register_and_login(client):
    """測試註冊與登入流程"""
    # 測試註冊
    reg_res = client.post('/api/auth/register', json={
        "username": "new_user",
        "password": "123"
    })
    assert reg_res.status_code == 201

    # 測試重複註冊防呆
    reg_res_dup = client.post('/api/auth/register', json={
        "username": "new_user",
        "password": "123"
    })
    assert reg_res_dup.status_code == 409

    # 測試登入拿 Token
    login_res = client.post('/api/auth/login', json={
        "username": "new_user",
        "password": "123"
    })
    assert login_res.status_code == 200
    assert 'access_token' in login_res.get_json()


# ==========================================
# 3. 藥袋 CRUD 測試 (使用 Mock 隔離外部依賴)
# ==========================================

def test_create_prescription_without_token(client):
    """測試未授權的存取，應該被系統阻擋"""
    response = client.post('/api/prescriptions')
    assert response.status_code == 401 # 401 Unauthorized


# 面試亮點：使用 @patch 來 Mock (攔截) 耗時的 OCR 處理程序
@patch('app.routes.scan_prescription')
@patch('app.routes.parse_da_pharmacy')
def test_create_prescription_with_token(mock_parse, mock_scan, client, auth_headers):
    """測試帶有 Token 的合法影像上傳"""
    
    # 設定當程式碼執行到這兩個函數時，直接回傳我們設定的「假資料」，不要真的去跑 OCR
    mock_scan.return_value = "這是假裝辨識出來的原始文字"
    mock_parse.return_value = {
        "patient_name": "王大明",
        "medicine_ch_name": "測試用藥"
    }

    # 模擬圖片檔案上傳 (使用 io.BytesIO 產生假檔案)
    data = {
        'file': (io.BytesIO(b"fake image content"), 'test_prescription.jpg')
    }

    # 發出 POST 請求，記得帶上我們的 auth_headers 萬能鑰匙！
    response = client.post(
        '/api/prescriptions', 
        data=data, 
        headers=auth_headers, 
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data['message'] == "資源建立並辨識成功"
    assert res_data['data']['patient_name'] == "王大明"



'''
import sys
import os
# 確保 Python 搜尋路徑包含專案根目錄
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
    response = client.post('/api/prescriptions')
    #測試沒登入
    assert response.status_code == 401
    #assert response.json['error'] == '請上傳圖片檔案'
'''