# OpenAI API 設置指南

## 概述

植物日記應用程式使用 OpenAI 的 Vision API 來分析植物照片，自動判斷植物狀態並提供照顧建議。

## 一、申請 OpenAI API Key

### 步驟 1：註冊 OpenAI 帳號

1. 前往 OpenAI 官方網站：https://platform.openai.com/
2. 點擊右上角的「Sign up」（註冊）或「Log in」（登入）
3. 如果沒有帳號，需要：
   - 輸入電子郵件地址
   - 設置密碼
   - 驗證電子郵件
   - 完成手機驗證

### 步驟 2：登入並進入 API 頁面

1. 登入後，點擊右上角的個人頭像
2. 選擇「View API keys」（查看 API 密鑰）
3. 或直接訪問：https://platform.openai.com/api-keys

### 步驟 3：創建 API Key

1. 點擊「Create new secret key」（創建新的密鑰）
2. 輸入一個名稱（例如：「植物日記」）
3. 點擊「Create secret key」（創建密鑰）
4. **重要**：立即複製並保存 API Key，因為之後無法再次查看完整密鑰
5. 將 API Key 保存在安全的地方

### 步驟 4：充值帳號（如需要）

1. 點擊右上角的帳號選單
2. 選擇「Billing」（帳單）
3. 點擊「Add payment method」（添加付款方式）
4. 輸入信用卡信息（支持 Visa、MasterCard 等）
5. 設置使用預算限制（可選，建議設置以避免意外費用）

**注意**：OpenAI 通常會提供一定額度的免費試用，之後按使用量付費。

## 二、選擇合適的模型

### 當前推薦模型：GPT-4o 或 GPT-4 Turbo

植物日記應用程式目前使用 **GPT-4o** 模型（在 `plant_diary/ai_analyzer.py` 中配置）。

### 模型比較

| 模型 | 特點 | 適用場景 | 成本 |
|------|------|----------|------|
| **GPT-4o** | 最新的多模態模型，視覺分析能力強 | **推薦用於植物照片分析** | 中等 |
| **GPT-4 Turbo** | 視覺分析能力強，速度快 | 適合植物照片分析 | 中等 |
| **GPT-4 Vision** | 專門優化的視覺模型 | 適合視覺分析任務 | 中等 |
| **GPT-3.5 Turbo** | 價格便宜，但無視覺能力 | ❌ 不適合（不支持圖像） | 低 |

### 為什麼選擇 GPT-4o？

1. **視覺分析能力強**：專門優化用於理解和分析圖像
2. **植物識別準確**：能夠識別植物種類、健康狀態、病蟲害等
3. **專業建議**：能夠提供詳細的照顧建議
4. **多語言支持**：支持繁體中文輸出
5. **成本合理**：相比 GPT-4 更經濟，性能相近

### 模型價格參考（2024年）

- **GPT-4o**：
  - 輸入：約 $2.50 / 1M tokens
  - 輸出：約 $10.00 / 1M tokens
  - 每次分析植物照片大約使用 500-1000 tokens

- **GPT-4 Turbo**：
  - 輸入：約 $10.00 / 1M tokens
  - 輸出：約 $30.00 / 1M tokens

**估算成本**：分析一張植物照片大約需要 $0.01-0.02（視圖片大小而定）

## 三、設置 API Key

### 方法 1：使用設置腳本（最簡單，推薦）

1. 雙擊運行 `plant_diary_web/設置OpenAI_API密鑰.bat`
2. 按照提示輸入您的 API 密鑰
3. 設置完成後，重新啟動 PowerShell 或命令提示符
4. 之後每次使用應用程式時，環境變數都會自動生效

### 方法 2：手動設置永久環境變數

#### Windows PowerShell：

```powershell
# 永久設置（用戶級別，需重新啟動終端後生效）
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-api-key-here', 'User')
```

設置完成後，**關閉並重新打開 PowerShell**，環境變數就會生效。

#### Windows 命令提示符（CMD）：

```cmd
# 永久設置（需重新啟動終端後生效）
setx OPENAI_API_KEY "your-api-key-here"
```

設置完成後，**關閉並重新打開命令提示符**，環境變數就會生效。

#### 通過 Windows 系統設置界面：

1. 按 `Win + R`，輸入 `sysdm.cpl`，按 Enter
2. 點擊「高級」標籤
3. 點擊「環境變數」按鈕
4. 在「使用者變數」區域，點擊「新增」
5. 變數名稱：`OPENAI_API_KEY`
6. 變數值：輸入您的 API 密鑰
7. 點擊「確定」保存
8. 重新啟動 PowerShell 或命令提示符

### 方法 3：臨時設置（僅當前會話有效）

如果只想在當前 PowerShell 會話中使用：

```powershell
# 臨時設置（僅當前會話有效，關閉窗口後失效）
$env:OPENAI_API_KEY="your-api-key-here"
```

### 方法 2：在代碼中設置（不推薦，安全性較低）

如果需要，可以在代碼中直接設置（但建議使用環境變數）：

```python
import os
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'
```

## 四、驗證設置

### 測試 API Key 是否正確

1. 啟動應用程式：
   ```powershell
   cd plant_diary_web
   python app.py
   ```

2. 上傳一張植物照片

3. 查看服務器終端輸出：
   - 如果看到「AI 分析完成」，表示設置成功
   - 如果看到錯誤訊息，檢查 API Key 是否正確

### 常見錯誤及解決方法

1. **錯誤：Invalid API Key**
   - 解決：檢查 API Key 是否正確複製
   - 確保沒有多餘的空格

2. **錯誤：Insufficient quota**
   - 解決：檢查帳號是否有餘額
   - 前往 Billing 頁面檢查

3. **錯誤：Rate limit exceeded**
   - 解決：API 調用頻率過高，稍後再試
   - 免費帳號有速率限制

## 五、成本控制建議

1. **設置使用預算**：
   - 在 OpenAI 後台設置每月預算上限
   - 設置使用警報

2. **監控使用量**：
   - 定期查看 Usage 頁面
   - 了解每次分析的成本

3. **優化使用**：
   - 不需要時可以不設置 API Key（應用程式會使用基礎模式）
   - 只在需要 AI 分析時上傳照片

## 六、修改模型（可選）

如果您想嘗試其他模型，可以修改 `plant_diary/ai_analyzer.py`：

```python
# 找到這一行（約第 61 行）
model="gpt-4o",

# 可以改為：
model="gpt-4-turbo",  # 或其他支持的模型
```

**支持的模型**：
- `gpt-4o`（推薦）
- `gpt-4-turbo`
- `gpt-4-vision-preview`

## 七、API Key 安全注意事項

1. **不要將 API Key 提交到版本控制系統（Git）**
   - API Key 包含在 `.gitignore` 中
   - 不要將包含 API Key 的文件分享給他人

2. **定期輪換 API Key**
   - 如果懷疑 API Key 洩露，立即撤銷並創建新的

3. **使用環境變數**
   - 不要將 API Key 硬編碼在代碼中
   - 使用環境變數是最佳實踐

## 相關資源

- OpenAI 官方文檔：https://platform.openai.com/docs
- API 使用指南：https://platform.openai.com/docs/guides/vision
- 定價信息：https://openai.com/pricing
- API 密鑰管理：https://platform.openai.com/api-keys

## 技術支持

如果遇到問題，可以：
1. 查看應用程式服務器終端的錯誤訊息
2. 檢查 OpenAI 後台的 Usage 頁面
3. 查看 OpenAI 官方文檔和社區論壇


