# 藥袋影像辨識系統 (Prescription OCR System) - 後端 API

本專案是一個基於 Python Flask 與 MySQL 構建的後端系統，旨在接收使用者上傳的藥袋影像，儲存紀錄，並預留整合光學字元辨識 (OCR) 的介面，以自動解析藥袋上的用藥資訊。

##  目前已實作功能 (Phase 1)
* **架構建立**：採用 Factory Pattern 構建 Flask 應用程式。
* **資料庫整合**：透過 Flask-SQLAlchemy 介接 MySQL，並定義完整的關聯式資料表 (Users, Prescriptions, Medications)。
* **自動建表機制**：系統啟動時會自動檢查並建立缺少的資料表與預設管理員帳號。
* **影像上傳 API**：提供安全的圖片上傳接口，自動以 UUID 重新命名檔案防止覆蓋，並將上傳紀錄寫入資料庫。

## 🛠 技術堆疊 (Tech Stack)
* **後端框架**：Python 3.x, Flask
* **資料庫**：MySQL 8.0+
* **ORM 工具**：Flask-SQLAlchemy
* **資料庫驅動**：PyMySQL
* **跨域處理**：Flask-CORS

## 📁 專案目錄結構
Medicine/
├── app/
│   ├── __init__.py       # Flask 工廠函數與資料庫初始化
│   ├── models.py         # 資料庫 Schema 定義
│   ├── routes.py         # API 路由邏輯
│   └── recognition.py    # (待開發) 影像辨識模組
├── uploads/              # 存放使用者上傳的藥袋照片
├── config.py             # 環境變數與資料庫連線設定
├── requirements.txt      # 專案依賴套件清單
├── run.py                # 系統啟動進入點
└── README.md             # 專案說明文件



1. 安裝環境與套件
請確保系統已安裝 Python 3.x，接著在終端機執行：
pip install -r requirements.txt

2. 資料庫設定
確保 MySQL 服務已啟動。
建立一個名為 prescription_db 的空資料庫：
SQL
CREATE DATABASE prescription_db CHARACTER SET utf8mb4;

3. 確認 config.py 內的連線字串與你的 MySQL 帳號密碼相符。


📡 API 文件說明
1. 系統狀態測試
    Endpoint: /test

    Method: GET

    回傳成功範例:

    JSON
    {
        "message": "API 運作中",
        "status": "success"
    }
2. 上傳藥袋影像
    Endpoint: /api/upload

    Method: POST

    Content-Type: multipart/form-data

    參數:

    file: (File) 藥袋圖片檔案，僅支援 .jpg, .jpeg, .png。

    回傳成功範例:

    JSON
    {
        "image_url": "uuid-string.jpg",
        "message": "圖片上傳成功",
        "prescription_id": 1
    }