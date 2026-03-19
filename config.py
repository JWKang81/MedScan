import os
from dotenv import load_dotenv
# 載入 .env 檔案中的變數到系統環境中
load_dotenv()
class Config:
   
    # 密碼記得使用環境變數存
    # 優先讀取 .env 或 Docker 給的 DATABASE_URL
    # 如果找不到，就給一個預設的假連線或測試用資料庫
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://root:your_password_here@127.0.0.1/prescription_db'
    )
    
    '''
    # 1. 資料庫設定
    # 格式: mysql+pymysql://使用者名稱:密碼@主機位址:埠號/資料庫名稱
    '''
    # 關閉追蹤修改以節省記憶體
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. 安全金鑰 (用於 Session 或 JWT 加密)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string-for-medicine-app'
    
    # 3. 檔案上傳設定
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上傳大小為 16MB
    