# 初始化 Flask 實例與綁定資料庫
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger  #restful api
import os
from config import Config  
from flask_jwt_extended import JWTManager

# 實例化資料庫物件，暫不傳入 app
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 1. 載入配置 (建立 config.py)
    app.config.from_object(Config)

    # 設定 JWT 的密鑰 (記得把這個變數加到 .env 和 config.py 裡)
    app.config['JWT_SECRET_KEY'] = 'your-super-secret-jwt-key'
    # 初始化 JWT
    jwt = JWTManager(app)

    # Swagger UI 的基礎設定 (文件首頁)
    app.config['SWAGGER'] = {
        'title': '藥袋影像辨識系統 API (Prescription OCR API)',
        'uiversion': 3,
        'description': '提供前端上傳藥袋影像並進行 OCR 辨識，以及確認存檔的 RESTful API。'
    }

    # 2. 允許跨域請求 
    CORS(app)
    
    # 3. 初始化組件
    db.init_app(app)

    # 在這裡初始化 Swagger
    # 設定 Swagger 樣板，加入 JWT 認證支援
    swagger_template = {
      "swagger": "2.0",
      "info": {
        "title": "Medicine OCR API",
        "description": "藥袋辨識與建檔系統 API 文件",
        "version": "1.0.0"
      },
      "securityDefinitions": {
        "Bearer": {
          "type": "apiKey",
          "name": "Authorization",
          "in": "header",
          "description": "請輸入 JWT Token。格式：Bearer <你的Token> (注意 Bearer 後面有一個半形空格)"
        }
      }
    }
    swagger = Swagger(app, template=swagger_template)

    # 檢查有無存放照片地方
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # 4. 註冊路由 (Blueprint) routes裡面的
    from .routes import main_bp
    app.register_blueprint(main_bp)
    # auth_routes裡的
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    # 確保資料表存在 
    with app.app_context():
        # 這裡需要匯入 models 以便 SQLAlchemy 知道要建立哪些表
        from . import models 
        db.create_all()

    return app