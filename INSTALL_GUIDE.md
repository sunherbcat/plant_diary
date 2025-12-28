# 植物日記 - 安裝指南

## ⚡ 快速安裝（推薦）

在 PowerShell 中執行以下命令：

```powershell
python -m pip install --only-binary :all: -r plant_diary_requirements.txt
```

> **重要**：使用 `--only-binary :all:` 參數可以避免編譯問題，特別是在 Python 3.14 等新版本上。

## 📦 安裝內容

此命令會安裝以下套件：

- **Pillow** - 圖像處理庫
- **openai** - OpenAI API 客戶端（用於 AI 分析和 OCR）
- **easyocr** - OCR 文字識別庫（免費 OCR 功能）
- **torch** - PyTorch（EasyOCR 的依賴）
- 其他必要的依賴套件

## 🔧 如果遇到問題

### 問題：安裝時出現編譯錯誤

**解決方案**：使用 `--only-binary :all:` 參數強制使用預編譯包：

```powershell
python -m pip install --only-binary :all: -r plant_diary_requirements.txt
```

### 問題：網絡連接慢或超時

**解決方案**：使用國內鏡像源（如果在中國大陸）：

```powershell
python -m pip install --only-binary :all: -r plant_diary_requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 問題：只想要基本功能，不需要 OCR

**解決方案**：只安裝基礎套件：

```powershell
python -m pip install --only-binary :all: Pillow openai
```

然後在應用程式中使用 OpenAI API 進行 OCR 識別（需要設置 API 密鑰）。

## ✅ 驗證安裝

安裝完成後，可以驗證：

```powershell
python -c "import easyocr; print('EasyOCR OK')"
python -c "import openai; print('OpenAI OK')"
python -c "from PIL import Image; print('Pillow OK')"
```

## 📝 注意事項

1. **首次使用 EasyOCR**：首次運行時，EasyOCR 會自動下載語言模型文件（約 100-200MB），需要一些時間。

2. **磁盤空間**：完整安裝需要約 1-2 GB 的磁盤空間。

3. **Python 版本**：建議使用 Python 3.8 或更高版本。

## 🆘 需要幫助？

如果仍有問題，請查看 `安裝依賴說明.md` 獲取更詳細的故障排除指南。




