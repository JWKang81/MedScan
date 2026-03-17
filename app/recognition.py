import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

import re

def parse_tzu_chi_prescription(raw_text):
    # 初始化資料結構
    data = {
        "hospital": "台北慈濟醫院",
        "patient_name": None,
        "medicine_ch_name": None,
        "medicine_en_name": None,
        "total_quantity": None,
        "usage_instruction": None,
        "days": None,
        "indications": None,
        "side_effects": None,
        "dispensing_date": None
    }

    # 1. 擷取姓名 (通常在第一行或靠近左上角，找其後的性別標記)
    # 規則：找「王小花」這種出現在開頭且後面跟著性別的文字
    name_match = re.search(r"^([\u4e00-\u9fa5]{2,4})\s+[男女]", raw_text, re.MULTILINE)
    if name_match:
        data["patient_name"] = name_match.group(1)

    # 2. 擷取藥名 (介於「藥名」與「外觀」之間)
    # 藥袋通常會列出：{複方} 星號 英文名 (成分名) 中文名
    med_block = re.search(r"藥名\s+.*?\n(.*?)\n外觀", raw_text, re.DOTALL)
    if med_block:
        full_med_text = med_block.group(1).strip()
        # 分離英文與中文 (假設中文名在最後一行)
        lines = full_med_text.split('\n')
        data["medicine_en_name"] = lines[0].replace('★', '').strip()
        data["medicine_ch_name"] = lines[-1].strip()

    # 3. 擷取總量 (找「粒」前面的數字)
    qty_match = re.search(r"(\d+)\s*粒", raw_text)
    if qty_match:
        data["total_quantity"] = qty_match.group(1)

    # 4. 擷取用法與天數 (在「用法」區塊)
    # 範例：每天兩次，早晚飯後使用，每次 1 粒，共 14 天。
    usage_match = re.search(r"用法\s+(.*?)，共\s*(\d+)\s*天", raw_text)
    if usage_match:
        data["usage_instruction"] = usage_match.group(1).strip()
        data["days"] = usage_match.group(2)

    # 5. 擷取用途 (在「用途」區塊)
    indication_match = re.search(r"用途\s+(.*?)\n", raw_text)
    if indication_match:
        data["indications"] = indication_match.group(1).strip()

    # 6. 擷取副作用 (在「副作用」區塊)
    side_effect_match = re.search(r"副作用\s+(.*?)\n", raw_text, re.DOTALL)
    if side_effect_match:
        data["side_effects"] = side_effect_match.group(1).strip()

    # 7. 擷取調劑日期 (找 YYYY/MM/DD)
    date_match = re.search(r"調劑日期\s+(\d{4}/\d{2}/\d{2})", raw_text)
    if date_match:
        data["dispensing_date"] = date_match.group(1)

    return data

def scan_prescription(image_path):
    """
    接收圖片路徑，進行影像處理並回傳辨識出的文字
    """
    try:
        # 1. 使用 OpenCV 讀取圖片，進行預處理提升辨識率
        # 讀取圖片
        image = cv2.imread(image_path)
        
        # 轉為灰階
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 二值化（讓文字更黑，背景更白）
        # 如果藥袋反光嚴重，這步可以調整參數或暫時省略
        threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 2. 將 OpenCV 處理過的陣列轉回 PIL 格式供 Tesseract 使用
        processed_pil_img = Image.fromarray(threshold_img)

        # 3. 執行 OCR
        # lang='chi_tra+eng' 代表同時辨識繁體中文與英文
        text = pytesseract.image_to_string(processed_pil_img, lang='chi_tra+eng')

        return text

    except Exception as e:
        return f"辨識過程發生錯誤: {str(e)}"
    
