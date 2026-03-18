import os

class Config:
    # 這裡的邏輯是：優先讀取環境變數 DATABASE_URL。
    # 如果讀不到 (例如你在本機開發沒用 Docker)，就用後面的本機預設值。
    # 請將後面的本機預設值換成你原本 MySQL 的帳號密碼！
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://root:55410801@127.0.0.1/prescription_db'
    )
    '''
    # 1. 資料庫設定
    # 格式: mysql+pymysql://使用者名稱:密碼@主機位址:埠號/資料庫名稱
    # 請根據你的實際 MySQL 設定修改下方連線字串
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:55410801@localhost:3306/prescription_db?charset=utf8mb4'
    '''
    # 關閉追蹤修改以節省記憶體
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 2. 安全金鑰 (用於 Session 或 JWT 加密)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string-for-medicine-app'
    
    # 3. 檔案上傳設定
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上傳大小為 16MB
    