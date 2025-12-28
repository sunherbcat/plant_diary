#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速轉換 FairyFern_logo.jpg 為 SVG 格式的便捷腳本
"""

from jpg_to_svg_converter import convert_jpg_to_svg
from pathlib import Path

def main():
    """轉換 LOGO 文件"""
    # 輸入文件路徑
    input_file = Path("LOGO/FairyFern_logo.jpg")
    
    # 輸出文件路徑（可選，如果不指定則自動生成）
    output_file = Path("LOGO/FairyFern_logo_converted.svg")
    
    print("=" * 50)
    print("FairyFern LOGO 向量化轉換工具")
    print("=" * 50)
    print()
    
    # 檢查輸入文件是否存在
    if not input_file.exists():
        print(f"錯誤：找不到輸入文件 {input_file}")
        print("請確認文件路徑是否正確。")
        return
    
    try:
        # 轉換圖像
        # 您可以調整這些參數以獲得最佳效果：
        # - threshold: 二值化閾值（0-255），建議範圍 100-200
        # - invert: 如果是白底黑字的 LOGO，設為 True
        # - simplify: 是否簡化路徑，True 會生成更小的文件
        # - smooth: 是否平滑處理，True 會讓結果更平滑
        convert_jpg_to_svg(
            input_file,
            output_file,
            threshold=128,      # 可以根據需要調整（建議：100-200）
            invert=False,       # 如果是白底黑字，改為 True
            simplify=True,      # 簡化路徑，生成較小的文件
            smooth=True         # 平滑處理，結果更平滑
        )
        
        print()
        print("[成功] 轉換成功完成！")
        print(f"  輸出文件：{output_file}")
        print()
        print("提示：如果結果不理想，請嘗試調整 threshold 參數：")
        print("  - 數值較低（如 100）：保留更多細節")
        print("  - 數值較高（如 200）：過濾更多噪點")
        
    except Exception as e:
        print(f"錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

