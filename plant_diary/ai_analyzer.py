#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物日記 - AI 圖像分析模組
使用 AI 分析植物照片，判斷植物狀態並提供照顧建議
"""

import os
import base64
import json
from pathlib import Path


class AIAnalyzer:
    """AI 圖像分析器"""
    
    def __init__(self, api_key=None):
        """
        初始化 AI 分析器
        
        參數:
            api_key: OpenAI API 密鑰（可選，如果沒有則使用本地分析）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.use_openai = self.api_key is not None
    
    def analyze_plant_photo(self, image_path, chinese_name=None, scientific_name=None):
        """
        分析植物照片
        
        參數:
            image_path: 照片路徑
            chinese_name: 植物的中文名稱（可選）
            scientific_name: 植物的學名（可選）
            
        返回:
            dict: 包含 ai_analysis 和 care_suggestions 的字典
        """
        if not os.path.exists(image_path):
            return {
                "ai_analysis": "無法找到圖片文件",
                "care_suggestions": ""
            }
        
        if self.use_openai:
            return self._analyze_with_openai(image_path, chinese_name, scientific_name)
        else:
            return self._analyze_local(image_path, chinese_name, scientific_name)
    
    def _analyze_with_openai(self, image_path, chinese_name=None, scientific_name=None):
        """使用 OpenAI API 分析圖片"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            # 讀取圖片並轉換為 base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 構建植物信息文本
            plant_info = ""
            if chinese_name or scientific_name:
                plant_info = "\n\n植物信息：\n"
                if chinese_name:
                    plant_info += f"中文名稱：{chinese_name}\n"
                if scientific_name:
                    plant_info += f"學名：{scientific_name}\n"
            
            # 構建用戶提示
            user_prompt = "請簡潔地分析這張植物照片的狀態，並提供簡明的照顧建議。分析要簡短（100-150字），建議要具體（3-5個要點）。"
            if plant_info:
                user_prompt = f"{user_prompt}{plant_info}\n請根據以上植物信息，結合照片中的實際狀況，提供針對性的照顧建議。"
            
            # 調用 GPT-4 Vision API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位專業的植物學家和園藝專家。請仔細觀察植物照片，簡潔地分析植物的健康狀態。

要求：
1. 分析要簡潔明瞭，控制在100-150字以內
2. 重點關注：葉片狀態、生長狀況、明顯問題
3. 照顧建議要具體且簡潔，列出3-5個要點即可
4. 如果提供了植物名稱或學名，請根據該物種的特性給出專業的照顧建議
5. 用繁體中文回答，語言要簡潔專業"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
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
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            
            # 分割分析和建議，優先處理"照顧建議："或"建議："格式
            if "照顧建議：" in analysis_text:
                parts = analysis_text.split("照顧建議：", 1)
                ai_analysis = parts[0].strip()
                care_suggestions = parts[1].strip() if len(parts) > 1 else ""
            elif "建議：" in analysis_text:
                parts = analysis_text.split("建議：", 1)
                ai_analysis = parts[0].strip()
                care_suggestions = parts[1].strip() if len(parts) > 1 else ""
            elif "建議" in analysis_text:
                parts = analysis_text.split("建議", 1)
                ai_analysis = parts[0].strip()
                care_suggestions = parts[1].strip() if len(parts) > 1 else ""
            else:
                ai_analysis = analysis_text
                care_suggestions = ""
            
            return {
                "ai_analysis": ai_analysis,
                "care_suggestions": care_suggestions
            }
            
        except ImportError:
            return self._analyze_local(image_path, chinese_name, scientific_name)
        except Exception as e:
            return {
                "ai_analysis": f"AI 分析出錯：{str(e)}",
                "care_suggestions": "請檢查 API 密鑰設置或網絡連接"
            }
    
    def _analyze_local(self, image_path, chinese_name=None, scientific_name=None):
        """本地基礎分析（不使用 API）"""
        # 這是一個基礎的佔位實現
        # 實際應用中可以集成其他免費的圖像識別服務
        
        plant_info_note = ""
        if chinese_name or scientific_name:
            plant_info_note = "\n\n植物信息：\n"
            if chinese_name:
                plant_info_note += f"中文名稱：{chinese_name}\n"
            if scientific_name:
                plant_info_note += f"學名：{scientific_name}\n"
        
        return {
            "ai_analysis": f"""由於未設置 OpenAI API 密鑰，目前使用基礎分析模式。{plant_info_note}

要使用完整的 AI 分析功能，請：
1. 前往 https://platform.openai.com 註冊並獲取 API 密鑰
2. 設置環境變數 OPENAI_API_KEY，或在應用程式設置中輸入 API 密鑰

目前提供的基本功能：
- 照片記錄和時間線查看
- 植物信息管理
- 成長歷程追蹤""",
            "care_suggestions": """照顧建議（請手動記錄）：
1. 定期檢查植物狀態
2. 記錄澆水時間和頻率
3. 觀察葉片變化
4. 注意光照和溫度
5. 適時施肥"""
        }


def get_analyzer(api_key=None):
    """獲取 AI 分析器實例"""
    return AIAnalyzer(api_key=api_key)

