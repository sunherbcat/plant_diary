# JPG 轉 SVG 向量格式轉換器

這個應用程式可以幫助您將位圖格式（JPG/PNG）轉換為向量格式（SVG）。

## ⚠️ 重要：先安裝 Python

**如果您看到 "pip : 無法辨識" 的錯誤訊息，表示系統尚未安裝 Python。**

請先參考 `安裝說明.md` 文件來安裝 Python，然後再繼續以下步驟。

## 安裝依賴

Python 安裝完成後，請在 PowerShell 中執行以下命令來安裝所需的 Python 套件：

```powershell
python -m pip install -r requirements.txt
```

或者（如果 pip 已正確設置）：

```powershell
pip install -r requirements.txt
```

或者直接安裝：

```bash
pip install opencv-python Pillow numpy
```

## 使用方法

### 基本用法

```bash
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg
```

這會在相同目錄下創建 `FairyFern_logo.svg` 文件。

### 指定輸出文件

```bash
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg output.svg
```

### 進階選項

```bash
# 調整二值化閾值（0-255，數值越高，保留的細節越少）
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg --threshold=200

# 反轉顏色（適用於白底黑字的圖像）
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg --invert

# 不使用路徑簡化（保留更多細節，但文件更大）
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg --no-simplify

# 不使用圖像平滑處理
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg --no-smooth

# 組合使用多個選項
python jpg_to_svg_converter.py LOGO/FairyFern_logo.jpg output.svg --threshold=180 --invert
```

## 參數說明

- `--threshold=128`: 二值化閾值，範圍 0-255。數值越高，轉換時保留的細節越少。預設值為 128。
- `--invert`: 反轉顏色。適用於白底黑字的圖像，轉換為黑底白字。
- `--no-simplify`: 不使用路徑簡化，保留更多細節，但生成的 SVG 文件會更大。
- `--no-smooth`: 不使用圖像平滑處理，保留原始圖像的所有細節。

## 在 Python 程式碼中使用

```python
from jpg_to_svg_converter import convert_jpg_to_svg

# 基本使用
convert_jpg_to_svg("LOGO/FairyFern_logo.jpg")

# 自訂參數
convert_jpg_to_svg(
    "LOGO/FairyFern_logo.jpg",
    output_path="output.svg",
    threshold=200,
    invert=True,
    simplify=True
)
```

## 注意事項

1. 這個工具使用輪廓檢測方法，最適合用於簡單的圖形、標誌或線條圖。
2. 對於複雜的照片或漸變圖像，結果可能不如專業的向量化軟體。
3. 建議先用不同的 threshold 值測試，以獲得最佳效果。

