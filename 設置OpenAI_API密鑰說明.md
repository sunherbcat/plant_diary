# 永久設置 OpenAI API 密鑰說明

## 快速設置（推薦方法）

### 方法 1：使用設置腳本（最簡單）

1. 找到 `plant_diary_web/設置OpenAI_API密鑰.bat` 文件
2. **雙擊運行**這個文件
3. 按照提示輸入您的 OpenAI API 密鑰
4. 設置完成後，**重新啟動 PowerShell 或命令提示符窗口**
5. 之後每次使用應用程式時，環境變數都會自動生效

### 方法 2：使用 PowerShell 命令

打開 PowerShell（以管理員權限運行，可選），執行以下命令：

```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', '你的API密鑰', 'User')
```

**重要**：設置完成後，必須：
- 關閉所有現有的 PowerShell 窗口
- 重新打開 PowerShell
- 環境變數才會生效

### 方法 3：使用 CMD 命令

打開命令提示符（CMD），執行：

```cmd
setx OPENAI_API_KEY "你的API密鑰"
```

**重要**：設置完成後，必須：
- 關閉所有現有的 CMD 窗口
- 重新打開 CMD
- 環境變數才會生效

### 方法 4：通過 Windows 系統設置界面

1. 按 `Win + R` 鍵，輸入 `sysdm.cpl`，按 Enter
2. 點擊「**高級**」標籤
3. 點擊「**環境變數**」按鈕
4. 在「**使用者變數**」區域，點擊「**新增**」
5. 變數名稱：`OPENAI_API_KEY`
6. 變數值：輸入您的 API 密鑰（例如：`sk-...`）
7. 點擊「**確定**」保存所有對話框
8. **重新啟動 PowerShell 或命令提示符**

## 驗證設置是否成功

### 方法 1：在 PowerShell 中檢查

打開新的 PowerShell 窗口，執行：

```powershell
$env:OPENAI_API_KEY
```

如果顯示您的 API 密鑰（開頭是 `sk-`），說明設置成功。

### 方法 2：在 CMD 中檢查

打開新的 CMD 窗口，執行：

```cmd
echo %OPENAI_API_KEY%
```

如果顯示您的 API 密鑰，說明設置成功。

### 方法 3：啟動應用程式檢查

1. 運行 `啟動Web版.bat`
2. 如果看到「未檢測到 OpenAI API 密鑰」的提示，說明設置未生效
3. 如果沒有提示，說明環境變數已經設置成功

## 為什麼需要重新啟動終端？

Windows 的環境變數設置是分層的：
- **系統級別環境變數**：所有用戶都可以使用
- **用戶級別環境變數**：只有當前用戶可以使用

當您設置用戶級別的環境變數時：
- 新的進程會繼承新的環境變數
- 已經運行的進程（包括當前打開的 PowerShell/CMD）不會自動更新
- 因此需要關閉並重新打開終端窗口

## 常見問題

### Q: 設置後還是顯示「未檢測到 OpenAI API 密鑰」

**A**: 請確認：
1. 您已經**關閉並重新打開**了所有 PowerShell/CMD 窗口
2. 在**新的** PowerShell/CMD 窗口中運行 `啟動Web版.bat`
3. 使用 `echo %OPENAI_API_KEY%`（CMD）或 `$env:OPENAI_API_KEY`（PowerShell）檢查環境變數是否存在

### Q: 我不想重新啟動終端，有其他方法嗎？

**A**: 可以，但這只是臨時設置（僅當前會話有效）：

在 PowerShell 中：
```powershell
$env:OPENAI_API_KEY="你的API密鑰"
```

在 CMD 中：
```cmd
set OPENAI_API_KEY=你的API密鑰
```

然後在**同一個窗口**中運行 `python app.py`

### Q: 如何獲取 OpenAI API 密鑰？

**A**: 請參考 `OpenAI_API設置指南.md` 文件，其中有詳細說明。

### Q: 環境變數設置後會一直有效嗎？

**A**: 是的，一旦設置為用戶級別的環境變數，它會一直有效，直到您：
- 手動刪除它
- 重新安裝 Windows
- 刪除用戶帳戶

## 安全提示

- API 密鑰是敏感信息，請不要分享給他人
- 不要在代碼中硬編碼 API 密鑰
- 如果 API 密鑰洩露，請立即到 OpenAI 平台撤銷並創建新的密鑰



