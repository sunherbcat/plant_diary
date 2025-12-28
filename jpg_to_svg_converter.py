#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JPG 轉 SVG 向量格式轉換器
將位圖格式（JPG/PNG）轉換為向量格式（SVG）
"""

import os
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import cv2


def preprocess_image(image_path, threshold=128, invert=False):
    """
    預處理圖像：轉換為灰度、二值化
    """
    # 讀取圖像
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"無法讀取圖像: {image_path}")
    
    # 轉換為灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 如果需要反轉（白底黑字轉黑底白字）
    if invert:
        gray = cv2.bitwise_not(gray)
    
    # 二值化
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    return binary, img.shape


def trace_image_to_svg(binary_image, original_shape, output_path, simplify=True, smooth=True):
    """
    將二值化圖像轉換為 SVG 向量格式
    使用輪廓檢測和路徑簡化
    """
    # 如果需要平滑，先進行形態學操作
    if smooth:
        kernel = np.ones((3,3), np.uint8)
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
    
    # 尋找輪廓（使用 RETR_TREE 來處理嵌套輪廓）
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # 創建 SVG
    width, height = original_shape[1], original_shape[0]
    svg_parts = [f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .shape {{ fill: black; stroke: none; }}
    </style>
  </defs>''']
    
    path_count = 0
    # 組織輪廓：將外輪廓和其內輪廓配對
    # 先找出所有外輪廓（parent = -1）
    outer_contours = []
    for i, contour in enumerate(contours):
        if len(contour) < 3:
            continue
        parent_idx = hierarchy[0][i][3]
        if parent_idx == -1:  # 外輪廓
            outer_contours.append(i)
    
    # 為每個外輪廓收集其內輪廓
    for outer_idx in outer_contours:
        group = [contours[outer_idx]]
        
        # 查找屬於此外輪廓的內輪廓（直接子輪廓）
        for i, contour in enumerate(contours):
            if len(contour) < 3:
                continue
            if hierarchy[0][i][3] == outer_idx:  # 這是 outer_idx 的直接子輪廓
                group.append(contour)
        
        # 生成 SVG 路徑
        path_parts = []
        for contour in group:
            # 簡化輪廓（可選）
            if simplify:
                epsilon = max(1.0, 0.01 * cv2.arcLength(contour, True))
                contour = cv2.approxPolyDP(contour, epsilon, True)
            
            # 轉換為 SVG 路徑段
            contour_path = []
            for j, point in enumerate(contour):
                x, y = point[0]
                if j == 0:
                    contour_path.append(f"M {x:.2f} {y:.2f}")
                else:
                    contour_path.append(f"L {x:.2f} {y:.2f}")
            contour_path.append("Z")
            path_parts.append(" ".join(contour_path))
        
        # 將外輪廓和內輪廓合併為一個路徑
        path_string = " ".join(path_parts)
        # 如果有多個輪廓（外輪廓+內輪廓），使用 evenodd 填充規則
        fill_rule = "evenodd" if len(group) > 1 else "nonzero"
        svg_parts.append(f'  <path d="{path_string}" class="shape" fill-rule="{fill_rule}"/>')
        path_count += len(group)
    
    svg_parts.append('</svg>')
    svg_content = "\n".join(svg_parts)
    
    # 寫入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return path_count


def convert_jpg_to_svg(input_path, output_path=None, threshold=128, invert=False, simplify=True, smooth=True):
    """
    將 JPG 圖像轉換為 SVG 向量格式
    
    參數:
        input_path: 輸入圖像路徑
        output_path: 輸出 SVG 路徑（如果為 None，則自動生成）
        threshold: 二值化閾值 (0-255)
        invert: 是否反轉顏色
        simplify: 是否簡化路徑
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")
    
    # 生成輸出路徑
    if output_path is None:
        output_path = input_path.with_suffix('.svg')
    else:
        output_path = Path(output_path)
    
    print(f"正在處理: {input_path}")
    print(f"輸出文件: {output_path}")
    
    # 預處理圖像
    binary_image, original_shape = preprocess_image(input_path, threshold, invert)
    
    # 轉換為 SVG
    num_contours = trace_image_to_svg(binary_image, original_shape, output_path, simplify, smooth)
    
    print(f"轉換完成！檢測到 {num_contours} 個輪廓")
    print(f"SVG 文件已保存至: {output_path}")
    
    return output_path


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方法: python jpg_to_svg_converter.py <輸入文件> [輸出文件] [選項]")
        print("\n選項:")
        print("  --threshold=128    二值化閾值 (0-255)")
        print("  --invert           反轉顏色（白底黑字轉黑底白字）")
        print("  --no-simplify      不使用路徑簡化")
        print("  --no-smooth        不使用圖像平滑處理")
        print("\n範例:")
        print("  python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg")
        print("  python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg --threshold=200 --invert")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = None
    threshold = 128
    invert = False
    simplify = True
    smooth = True
    
    # 解析參數
    for arg in sys.argv[2:]:
        if arg.startswith("--threshold="):
            threshold = int(arg.split("=")[1])
        elif arg == "--invert":
            invert = True
        elif arg == "--no-simplify":
            simplify = False
        elif arg == "--no-smooth":
            smooth = False
        elif not arg.startswith("--"):
            output_path = arg
    
    try:
        convert_jpg_to_svg(input_path, output_path, threshold, invert, simplify, smooth)
    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

