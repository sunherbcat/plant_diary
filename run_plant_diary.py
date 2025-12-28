#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物日記啟動腳本
"""

import sys
import os
from pathlib import Path

# 確保在正確的目錄中運行
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

# 添加當前目錄到路徑
sys.path.insert(0, str(script_dir))

# 導入主程式
if __name__ == "__main__":
    # 嘗試兩種導入方式
    try:
        from plant_diary.main import main
    except ImportError:
        # 如果作為包導入失敗，嘗試直接導入模組
        plant_diary_path = script_dir / "plant_diary"
        if plant_diary_path.exists():
            sys.path.insert(0, str(plant_diary_path))
            from main import main
        else:
            print("錯誤：找不到 plant_diary 目錄")
            sys.exit(1)
    
    main()

