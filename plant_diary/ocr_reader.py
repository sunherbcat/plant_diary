#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物日記 - OCR 文字識別模組
從植物花牌照片中識別中文名稱和學名
"""

import os
import tempfile
from pathlib import Path
import re


class OCRReader:
    """OCR 文字識別器"""
    
    def __init__(self):
        """初始化 OCR 識別器"""
        self.easyocr_available = False
        self.openai_available = False
        self._init_easyocr()
    
    def _init_easyocr(self):
        """初始化 EasyOCR"""
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            self.easyocr_available = True
        except ImportError:
            self.easyocr_available = False
        except Exception as e:
            print(f"EasyOCR 初始化失敗: {e}")
            self.easyocr_available = False
    
    def recognize_text(self, image_path, use_openai=False, openai_api_key=None):
        """
        識別圖片中的文字
        
        參數:
            image_path: 圖片路徑
            use_openai: 是否使用 OpenAI API（更準確）
            openai_api_key: OpenAI API 密鑰
            
        返回:
            dict: 包含識別結果的字典
                - chinese_name: 中文名稱
                - scientific_name: 學名
                - raw_text: 原始識別文字
                - success: 是否成功
                - error: 錯誤訊息
        """
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": "圖片文件不存在",
                "chinese_name": "",
                "scientific_name": "",
                "raw_text": ""
            }
        
        if use_openai and openai_api_key:
            return self._recognize_with_openai(image_path, openai_api_key)
        elif self.easyocr_available:
            return self._recognize_with_easyocr(image_path)
        else:
            return {
                "success": False,
                "error": "未安裝 OCR 庫。請安裝 easyocr 或設置 OpenAI API 密鑰",
                "chinese_name": "",
                "scientific_name": "",
                "raw_text": ""
            }
    
    def _recognize_with_openai(self, image_path, api_key):
        """使用 OpenAI Vision API 識別文字"""
        try:
            from openai import OpenAI
            import base64
            
            client = OpenAI(api_key=api_key)
            
            # 讀取圖片並轉換為 base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 調用 GPT-4 Vision API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一個專業的OCR識別系統。請從植物花牌照片中識別以下信息：
1. 中文名稱（繁體中文）
2. 英文學名（Scientific name，通常是斜體或特殊格式的拉丁文）

請以JSON格式返回，格式如下：
{
    "chinese_name": "中文名稱",
    "scientific_name": "Scientific name"
}

如果某個信息無法識別，請使用空字符串。只返回JSON，不要返回其他文字。"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "請識別這張植物花牌照片中的中文名稱和學名。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 嘗試解析JSON
            try:
                import json
                # 移除可能的markdown代碼塊標記
                result_text = re.sub(r'```json\n?', '', result_text)
                result_text = re.sub(r'```\n?', '', result_text)
                result_text = result_text.strip()
                
                result_json = json.loads(result_text)
                chinese_name = result_json.get("chinese_name", "").strip()
                scientific_name = result_json.get("scientific_name", "").strip()
                
                return {
                    "success": True,
                    "error": "",
                    "chinese_name": chinese_name,
                    "scientific_name": scientific_name,
                    "raw_text": result_text
                }
            except json.JSONDecodeError:
                # 如果JSON解析失敗，嘗試直接提取
                return self._parse_text_manually(result_text)
                
        except ImportError:
            return {
                "success": False,
                "error": "未安裝 openai 庫",
                "chinese_name": "",
                "scientific_name": "",
                "raw_text": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API 錯誤: {str(e)}",
                "chinese_name": "",
                "scientific_name": "",
                "raw_text": ""
            }
    
    def _recognize_with_easyocr(self, image_path):
        """使用 EasyOCR 識別文字"""
        try:
            # 首先驗證圖片文件是否存在且可讀
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": "圖片文件不存在",
                    "chinese_name": "",
                    "scientific_name": "",
                    "raw_text": ""
                }
            
            # 使用 PIL 驗證圖片是否可以正確打開
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    # 驗證圖片是否有效
                    img.verify()
            except Exception as img_error:
                return {
                    "success": False,
                    "error": f"圖片文件損壞或格式不支持: {str(img_error)}",
                    "chinese_name": "",
                    "scientific_name": "",
                    "raw_text": ""
                }
            
            # 重新打開圖片（因為 verify 後需要重新打開）
            temp_path = None
            try:
                from PIL import Image
                img = Image.open(image_path)
                # 轉換為 RGB 模式（處理 RGBA 等模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # 保存為臨時文件（確保格式正確）
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                    img.save(tmp_file.name, 'JPEG', quality=95)
                    temp_path = tmp_file.name
            except Exception as img_error:
                return {
                    "success": False,
                    "error": f"圖片處理錯誤: {str(img_error)}",
                    "chinese_name": "",
                    "scientific_name": "",
                    "raw_text": ""
                }
            
            try:
                # 使用臨時文件進行識別
                results = self.easyocr_reader.readtext(temp_path)
                
                # 提取所有識別的文字
                all_text = []
                all_text_for_display = []  # 用於顯示的完整文本（包含過濾詞）
                
                for (bbox, text, confidence) in results:
                    # 降低置信度閾值，以獲取更多文字（0.2 而不是 0.3）
                    if confidence > 0.2 and text and text.strip():
                        text_clean = text.strip()
                        # 保存所有文本用於顯示
                        all_text_for_display.append(text_clean)
                        
                        # 預先定義的過濾詞（這些詞來自LOGO，不應該作為植物名稱）
                        # 包括 OCR 可能的誤識別變體（如「花圈」、「花圜」誤識別為「花園」）
                        filter_words = [
                            '童話', '花園', '花圈', '花圜',  # 花圈、花圜是花園的OCR誤識別
                            'QR', 'qr', 'code', 'Code', 'CODE',
                            '童話花園', '花園童話', '童話 花園', '花園 童話',
                            '童話花圈', '花圈童話', '童話 花圈', '花圈 童話',  # 花圈的組合
                            '童話花圜', '花圜童話', '童話 花圜', '花圜 童話'  # 花圜的組合
                        ]
                        # 預先過濾：如果只是過濾詞，不加入解析列表
                        if text_clean not in filter_words:
                            all_text.append(text_clean)
                
                # 原始文本包含所有識別到的文字（用於顯示給用戶看）
                raw_text = "\n".join(all_text_for_display) if all_text_for_display else ""
                
                # 調試信息
                print(f"OCR識別到的文本列表: {all_text}")
                print(f"OCR原始文本: {raw_text}")
                
                # 解析文字，識別中文名稱和學名
                chinese_name, scientific_name = self._parse_plant_info(all_text)
                
                print(f"解析結果 - 中文名稱: {chinese_name}, 學名: {scientific_name}")
                
                return {
                    "success": True,
                    "error": "",
                    "chinese_name": chinese_name,
                    "scientific_name": scientific_name,
                    "raw_text": raw_text
                }
            finally:
                # 清理臨時文件
                try:
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception:
                    pass
            
        except Exception as e:
            return {
                "success": False,
                "error": f"EasyOCR 識別錯誤: {str(e)}",
                "chinese_name": "",
                "scientific_name": "",
                "raw_text": ""
            }
    
    def _parse_plant_info(self, text_list):
        """
        從識別的文字列表中解析植物信息
        
        參數:
            text_list: 文字列表
            
        返回:
            tuple: (chinese_name, scientific_name)
        """
        chinese_name = ""
        scientific_name = ""
        
        # 過濾詞列表（這些詞不應該作為植物名稱，來自LOGO）
        # 包括 OCR 可能的誤識別變體（如「花圈」、「花圜」誤識別為「花園」）
        filter_words = [
            '童話', '花園', '花圈', '花圜',  # 花圈、花圜是花園的OCR誤識別
            'QR', 'qr', 'code', 'Code', 'CODE',
            '童話花園', '花園童話', '童話花圈', '花圈童話', '童話花圜', '花圜童話'
        ]
        
        # 查找中文名稱（通常包含中文漢字）
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        for text in text_list:
            text_clean = text.strip()
            
            # 檢查是否包含中文字符
            if chinese_pattern.search(text_clean):
                # 如果整個文本就是過濾詞，則跳過
                if text_clean in filter_words:
                    continue
                
                # 如果文本只包含"童話"和"花園"/"花圈"/"花圜"的組合，則跳過
                if text_clean in ['童話花園', '花園童話', '童話 花園', '花園 童話',
                                  '童話花圈', '花圈童話', '童話 花圈', '花圈 童話',
                                  '童話花圜', '花圜童話', '童話 花圜', '花圜 童話']:
                    continue
                
                # 如果文本只包含"童話"或"花園"/"花圈"/"花圜"其中一個字，且長度很短，則跳過
                if text_clean in ['童', '話', '花', '園', '圈', '圜', '童話', '花園', '花圈', '花圜']:
                    continue
                
                # 移除開頭和結尾的過濾詞
                filtered = text_clean
                for word in filter_words:
                    # 移除開頭的過濾詞
                    filtered = re.sub(rf'^{re.escape(word)}[\s]*', '', filtered, flags=re.IGNORECASE)
                    # 移除結尾的過濾詞
                    filtered = re.sub(rf'[\s]*{re.escape(word)}$', '', filtered, flags=re.IGNORECASE)
                
                # 移除中間的"童話"和"花園"/"花圈"/"花圜"組合
                filtered = re.sub(r'童話\s*花園', '', filtered, flags=re.IGNORECASE)
                filtered = re.sub(r'花園\s*童話', '', filtered, flags=re.IGNORECASE)
                filtered = re.sub(r'童話\s*花圈', '', filtered, flags=re.IGNORECASE)
                filtered = re.sub(r'花圈\s*童話', '', filtered, flags=re.IGNORECASE)
                filtered = re.sub(r'童話\s*花圜', '', filtered, flags=re.IGNORECASE)
                filtered = re.sub(r'花圜\s*童話', '', filtered, flags=re.IGNORECASE)
                # 移除中間單獨的"花圈"和"花圜"（OCR誤識別的"花園"）
                # 移除所有出現的"花圈"和"花圜"，無論前後是否有空格
                filtered = re.sub(r'花圈', '', filtered)
                filtered = re.sub(r'花圜', '', filtered)
                
                filtered = filtered.strip()
                
                # 如果過濾後還有內容，且包含中文字符，則作為中文名稱
                if len(filtered) > 0 and chinese_pattern.search(filtered):
                    # 進一步檢查：如果過濾後的文本仍然只包含過濾詞，則跳過
                    is_only_filtered = False
                    for word in filter_words:
                        # 檢查是否只包含過濾詞（允許一些空格）
                        if re.match(rf'^[\s]*{re.escape(word)}[\s]*$', filtered, flags=re.IGNORECASE):
                            is_only_filtered = True
                            break
                        # 如果文本很短（<=3個字符）且包含過濾詞，可能只是過濾詞，跳過
                        if len(filtered) <= 3 and word in filtered:
                            is_only_filtered = True
                            break
                    
                    if not is_only_filtered:
                        chinese_name = filtered
                        break
        
        # 查找學名（通常是拉丁文，包含空格和大小寫字母）
        # 學名格式通常是：Genus species 或 Genus species subspecies
        for text in text_list:
            text_clean = text.strip()
            
            # 跳過純中文文本
            if chinese_pattern.match(text_clean):
                continue
            
            # 檢查是否符合學名格式：首字母大寫的單詞，後面跟小寫單詞
            # 更寬鬆的匹配：允許包含特殊字符、點等
            # 例如：Anthurium veitchii, P. veitchii, etc.
            scientific_match = re.match(r'^[A-Z][a-zA-Z]*(?:\.[\s]*[A-Z][a-zA-Z]*)?[\s]+[a-z][a-zA-Z]*(?:\s+[a-z][a-zA-Z]*)*', text_clean)
            if scientific_match:
                potential_name = scientific_match.group(0).strip()
                # 確保長度合理（至少5個字符，不超過100個字符）
                if 5 <= len(potential_name) <= 100:
                    scientific_name = potential_name
                    break
        
        return chinese_name, scientific_name
    
    def _parse_text_manually(self, text):
        """手動解析文字（當JSON解析失敗時使用）"""
        chinese_name = ""
        scientific_name = ""
        
        # 查找中文
        chinese_match = re.search(r'[\u4e00-\u9fff]+', text)
        if chinese_match:
            chinese_name = chinese_match.group().strip()
        
        # 查找學名（拉丁文格式）
        scientific_match = re.search(r'([A-Z][a-z]+(?:\s+[a-z]+)+)', text)
        if scientific_match:
            scientific_name = scientific_match.group(1).strip()
        
        return {
            "success": True,
            "error": "",
            "chinese_name": chinese_name,
            "scientific_name": scientific_name,
            "raw_text": text
        }


def get_ocr_reader():
    """獲取 OCR 識別器實例"""
    return OCRReader()

