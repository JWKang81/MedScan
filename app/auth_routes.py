from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    使用者註冊系統
    提供帳號、密碼與電子信箱來建立新使用者。密碼將在後端進行雜湊加密。
    ---
    tags:
      - Authentication (認證授權)
    parameters:
      - in: body
        name: body
        required: true
        description: 註冊所需的帳號資訊
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 使用者帳號 (必須唯一)
              example: "interview_user"
            password:
              type: string
              description: 使用者密碼
              example: "my_secure_password"
            email:
              type: string
              description: 電子信箱 (選填)
              example: "user@example.com"
    responses:
      201:
        description: 註冊成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "註冊成功！"
      400:
        description: 缺少必填欄位 (帳號或密碼)
      409:
        description: 帳號已被註冊 (資料庫衝突)
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({"error": "帳號與密碼為必填欄位"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "此帳號已被註冊"}), 409 # 409 Conflict

    # 建立新使用者
    new_user = User(username=username, email=email)
    new_user.set_password(password) # 使用我們剛才封裝的方法！

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "註冊成功！"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    使用者登入並取得 JWT Token
    驗證帳號密碼後，核發可用於存取受保護 API 的 JWT (JSON Web Token)。
    ---
    tags:
      - Authentication (認證授權)
    parameters:
      - in: body
        name: body
        required: true
        description: 登入憑證
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "interview_user"
            password:
              type: string
              example: "my_secure_password"
    responses:
      200:
        description: 登入成功，回傳 JWT Token
        schema:
          type: object
          properties:
            message:
              type: string
              example: "登入成功"
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI..."
      401:
        description: 帳號或密碼錯誤 (授權失敗)
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    # 驗證帳號存在，且密碼正確
    if not user or not user.check_password(password):
        return jsonify({"error": "帳號或密碼錯誤"}), 401 # 401 Unauthorized

    # 登入成功，核發 JWT Token (可以把使用者 ID 塞在 token 裡)
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "登入成功",
        "access_token": access_token
    }), 200