# 1. 使用輕量級的 Python 3.9 作為基底
FROM python:3.9-slim

# 2. 設定容器內的工作目錄
WORKDIR /app

# 3. 安裝系統級別的依賴套件 (重點：安裝 Tesseract 與繁體中文包、OpenCV 所需的函式庫)
# (加入 --fix-missing 並分開執行以利排錯)
# 更換 libgl1-mesa-glx 為 libgl1，這是目前 Debian 版本的標準做法

RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. 複製套件清單並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 將你所有的程式碼複製進容器內
COPY . .

# 6. 宣告這個容器會使用 3000 Port
EXPOSE 3000

# 7. 容器啟動時要執行的指令
CMD ["python", "run.py"]