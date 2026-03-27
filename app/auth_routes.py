from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    使用者註冊
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
            email:
              type: string
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
    使用者登入並獲取 Token
    ---
    tags:
      - Authentication
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