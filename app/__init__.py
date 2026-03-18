# 初始化 Flask 實例與綁定資料庫
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger  #restful api
import os
from config import Config  

# 實例化資料庫物件，暫不傳入 app
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 1. 載入配置 (建立 config.py)
    # 如果還沒建立 config.py，暫時可用下面這行簡單測試
    app.config.from_object(Config)

    # Swagger UI 的基礎設定 (這會顯示在文件首頁)
    app.config['SWAGGER'] = {
        'title': '藥袋影像辨識系統 API (Prescription OCR API)',
        'uiversion': 3,
        'description': '提供前端上傳藥袋影像並進行 OCR 辨識，以及確認存檔的 RESTful API。'
    }

    # 2. 允許跨域請求 (前端開發必備)
    CORS(app)
    
    # 3. 初始化組件
    db.init_app(app)

    # 在這裡初始化 Swagger
    Swagger(app)
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # 4. 註冊路由 (Blueprint)
    # 這裡預留：等我們寫好 routes.py 後再回來取消註解
    # from .routes import main_bp
    # app.register_blueprint(main_bp)
    # 4. 註冊路由 (Blueprint)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # 確保資料表存在 (開發初期很好用，會自動根據 models.py 建立欄位)
    with app.app_context():
        # 這裡需要匯入 models 以便 SQLAlchemy 知道要建立哪些表
        from . import models 
        db.create_all()

    return app