import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

import re

import pytesseract
from PIL import Image
import cv2
import re

def parse_da_pharmacy(raw_text):
    """
    專為「大藥局」藥袋 (005.jpg) 設計的正則表達式解析器
    """
    data = {
        "hospital": "大藥局",
        "patient_name": "",
        "medicine_ch_name": "",
        "medicine_en_name": "",
        "total_quantity": "",
        "usage_instruction": "",
        "days": 0,
        "indications": "",
        "side_effects": "",
        "dispensing_date": ""
    }

    # 1. 擷取姓名 (尋找「姓名：」後方的文字)
    name_match = re.search(r"姓\s*名\s*[:：]\s*([\u4e00-\u9fa5]{2,4})", raw_text)
    if name_match:
        data["patient_name"] = name_match.group(1)

    # 2. 擷取日期 (尋找「日期/時間：」後方的數字與斜線)
    date_match = re.search(r"日期.*?時間\s*[:：]?\s*([\d/]+)", raw_text)
    if date_match:
        data["dispensing_date"] = date_match.group(1)

    # 3. 擷取天數 (尋找「處方天數：」後方的數字)
    days_match = re.search(r"處方天數\s*[:：]?\s*(\d+)", raw_text)
    if days_match:
        data["days"] = int(days_match.group(1))

    # 4. 擷取總量 (尋找「發藥量：」後方的數字)
    qty_match = re.search(r"發\s*藥\s*量\s*[:：]?\s*([\d.]+)", raw_text)
    if qty_match:
        data["total_quantity"] = qty_match.group(1)

    # 5. 擷取用法用量 (抓取「用法用量」到「Usage」或「處方天數」之間的內容)
    # 使用 re.S (DOTALL) 允許跨行比對
    usage_match = re.search(r"用法用量\s*[:：]?\s*(.*?)(?=Usage|處方天數)", raw_text, re.S | re.IGNORECASE)
    if usage_match:
        # 去除多餘的換行符號，組合成單行字串
        data["usage_instruction"] = " ".join(usage_match.group(1).split())

    # 6. 擷取藥名 (抓取「藥名」到「發藥量」或「Drug Name」之間的內容)
    med_match = re.search(r"藥\s*名\s*[:：]?\s*(.*?)(?=發\s*藥\s*量|Drug Name)", raw_text, re.S | re.IGNORECASE)
    if med_match:
        med_text = med_match.group(1).strip()
        # 大藥局的藥名通常包含中英文，並用斜線 '/' 分隔
        if '/' in med_text:
            parts = med_text.split('/', 1)
            data["medicine_ch_name"] = parts[0].replace('\n', '').strip()
            data["medicine_en_name"] = parts[1].replace('\n', '').strip()
        else:
            data["medicine_ch_name"] = med_text.replace('\n', '').strip()

    # 7. 擷取副作用 (對應單子上的「藥物作用」)
    side_effect_match = re.search(r"藥物作用\s*[:：]?\s*(.*?)(?=Clinical Uses|注意事項)", raw_text, re.S | re.IGNORECASE)
    if side_effect_match:
        data["side_effects"] = " ".join(side_effect_match.group(1).split())

    # 8. 擷取適應症 (對應單子上的「Clinical Uses」)
    indication_match = re.search(r"Clinical Uses\s*[:：]?\s*(.*?)(?=注意事項|Precautions)", raw_text, re.S | re.IGNORECASE)
    if indication_match:
        data["indications"] = " ".join(indication_match.group(1).split())

    return data


def scan_prescription(image_path):
    """
    接收圖片路徑，進行影像處理並回傳解析後的資料字典
    """
    try:
        # 1. 影像預處理
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        processed_pil_img = Image.fromarray(threshold_img)

        # 2. 執行 OCR
        raw_text = pytesseract.image_to_string(processed_pil_img, lang='chi_tra+eng')
        
        # 可在終端機印出原始文字供除錯參考
        print("\n=== OCR 原始文字 ===")
        print(raw_text)
        print("====================\n")
        return raw_text
        # 3. 使用專屬解析器萃取資料
        extracted_data = parse_da_pharmacy(raw_text)

        return {
            "status": "success",
            "data": extracted_data,
            "raw_text": raw_text
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"辨識過程發生錯誤: {str(e)}"
        }