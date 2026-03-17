
# 定義 MySQL 資料表結構 (Users, Prescriptions...)
from datetime import datetime
# 假設你在 app/__init__.py 已經初始化了 db = SQLAlchemy()
from app import db 

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='使用者帳號')
    password_hash = db.Column(db.String(255), nullable=False, comment='加密後的密碼')
    email = db.Column(db.String(100), unique=True, nullable=True, comment='電子信箱')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='註冊時間')
    
    # 建立與藥單的關聯 (One-to-Many)
    prescriptions = db.relationship('Prescription', backref='user', lazy=True)

class Prescription(db.Model):
    """藥單/藥袋主檔：負責記錄這次上傳的影像與整體資訊"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='關聯的使用者ID')
    
    image_path = db.Column(db.String(255), nullable=False, comment='影像在伺服器上的儲存路徑')
    hospital_name = db.Column(db.String(100), nullable=True, comment='醫療院所名稱')
    patient_name = db.Column(db.String(50), nullable=True, comment='病患姓名(可由OCR辨識)')
    dispense_date = db.Column(db.Date, nullable=True, comment='調劑日期')
    
    # 狀態控管非常重要：辨識中(processing)、待確認(pending_review)、已確認(confirmed)
    status = db.Column(db.String(20), default='processing', comment='辨識與確認狀態') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='上傳時間')
    
    # 建立與藥品明細的關聯 (One-to-Many)
    medications = db.relationship('Medication', backref='prescription', cascade="all, delete-orphan", lazy=True)

class Medication(db.Model):
    """藥品明細檔：記錄從該張藥袋中辨識出來的每一項藥品"""
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False, comment='關聯的藥單ID')
    
    # 這些是 OCR 辨識的主要目標欄位
    medicine_name = db.Column(db.String(150), nullable=False, comment='藥品名稱(中/英文)')
    dosage = db.Column(db.String(50), nullable=True, comment='每次用量 (如: 1顆, 10ml)')
    frequency = db.Column(db.String(50), nullable=True, comment='使用頻率 (如: 一天三次, 飯後)')
    days = db.Column(db.Integer, nullable=True, comment='給藥天數')
    total_amount = db.Column(db.String(50), nullable=True, comment='總量 (如: 21顆)')
    indications = db.Column(db.String(255), nullable=True, comment='適應症/用途 (如: 止痛、退燒)')
    side_effects = db.Column(db.String(255), nullable=True, comment='副作用(如: 疲倦)')

    # 允許標記這個藥品是否有被使用者手動修改過 (衡量辨識準確度的指標)
    is_edited = db.Column(db.Boolean, default=False, comment='使用者是否手動校正過')