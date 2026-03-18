# Medicine Prescription OCR System (藥袋影像辨識與建檔系統)

[![CI/CD](https://github.com/JWKang81/Medicine/actions/workflows/ci.yml/badge.svg)](https://github.com/你的GitHub帳號/Medicine/actions)
[![Python Version](https://img.shields.io/badge/python-3.9-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://www.docker.com/)
[![Swagger API](https://img.shields.io/badge/API-Swagger%20OpenAPI-85EA2D.svg)](http://localhost:3000/apidocs/)

這是一個基於 Flask 開發的 RESTful API 服務，旨在透過 Tesseract OCR 技術自動擷取藥袋上的關鍵資訊（如：病患姓名、藥品名稱、用藥指示等），並將結構化的資料儲存至關聯式資料庫中。

本專案嚴格遵循**現代軟體工程實踐 (Software Engineering Practices)**，具備完整的自動化測試、容器化部署與持續整合流程。

---

## 技術實踐

* **Backend Framework**: Python 3.9, Flask (Blueprint 架構)
* **REST API & Documentation**: 遵循 RESTful 設計準則，並整合 `Flasgger` 提供符合 OpenAPI (Swagger) 規範的互動式 API 文件。
* **Optical Character Recognition (OCR)**: 整合 `Tesseract` 與 `OpenCV`，搭配 Regular Expression (正規表達式) 進行文字清洗與特徵萃取。
* **Database**: MySQL 8.0, SQLAlchemy ORM (支援防範 SQL Injection 與連線池管理)。
* **Containerization**: 撰寫 `Dockerfile` 與 `docker-compose.yml`，將應用程式、資料庫與 OCR 引擎完整封裝，確保跨平台環境一致性。
* **Software Engineering Practices**:
  * **TDD (Test-Driven Development)**: 使用 `pytest` 實作單元測試，並運用 SQLite 記憶體資料庫確保測試的隔離性與執行速度。
  * **CI/CD Pipeline**: 透過 GitHub Actions 建立持續整合管線，實現自動化依賴安裝、測試驗證與 Docker 構建測試。

---

##  快速啟動 (Getting Started)

透過 Docker Compose，您可以一鍵啟動整個系統，無需在本地端手動安裝資料庫或 OCR 引擎。

### 1. 環境要求 (Prerequisites)
* 安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Git

### 2. 啟動步驟 (Installation & Execution)

```bash
# 複製專案原始碼
git clone [https://github.com/JWKang81/Medicine.git](https://github.com/JWKang81/Medicine.git)
cd Medicine

# 使用 Docker Compose 一鍵建置並啟動服務 (包含 Web 與 MySQL)
docker compose up --build -d