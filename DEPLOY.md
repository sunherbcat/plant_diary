# 植物日記部署指南

這是植物日記應用的簡化部署指南，幫助您快速將應用部署到網路伺服器。

## 🎯 推薦方案：Render.com（最簡單，免費）

### 步驟 1：確認文件已準備

您的項目應該包含以下文件：
- ✅ `plant_diary_web/app.py` - Web 應用主文件
- ✅ `plant_diary_web/Procfile` - 部署配置文件
- ✅ `plant_diary_web/requirements.txt` - Python 依賴列表
- ✅ `plant_diary_web/runtime.txt` - Python 版本
- ✅ `plant_diary/` - 應用核心模組

### 步驟 2：在 Render 創建應用

1. **訪問 Render.com**
   - 前往 https://render.com
   - 使用 GitHub 帳號登入或註冊

2. **連接 Git 倉庫**
   - 點擊 "New +" → "Web Service"
   - 選擇您的 GitHub 倉庫（`plant_diary`）

3. **配置設置**

   **基本設置：**
   ```
   Name: plant-diary（或您喜歡的名稱）
   Region: 選擇離您最近的區域
   Branch: main（或您的默認分支）
   Root Directory: 留空（應用在根目錄）
   ```

   **構建和啟動命令：**
   ```
   Build Command: pip install -r plant_diary_web/requirements.txt
   Start Command: cd plant_diary_web && gunicorn app:app --bind 0.0.0.0:$PORT
   ```

   **Python 版本：**
   - Render 會自動檢測 `runtime.txt`，或手動選擇 Python 3.11

4. **添加環境變數**

   在 Environment 區段添加：
   ```
   SECRET_KEY: [生成一個隨機字符串]
   OPENAI_API_KEY: [您的 OpenAI API 密鑰，可選]
   FLASK_ENV: production
   ```

   **生成 SECRET_KEY：**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```
   或在命令行執行：
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **創建並部署**
   - 點擊 "Create Web Service"
   - 等待構建完成（約 5-10 分鐘）
   - 首次構建可能需要更長時間（因為要安裝 easyocr 等大型依賴）

6. **獲取 URL**
   - 部署成功後，您會獲得一個 URL，例如：
   - `https://plant-diary-xxxx.onrender.com`

### ⚠️ 重要注意事項

#### 數據持久化問題

Render 免費層的本地文件系統在重啟時會重置，這意味著：
- ❌ SQLite 數據庫會被重置
- ❌ 上傳的照片會丟失

**解決方案選項：**

1. **使用 Render PostgreSQL（推薦）**
   - 在 Render 創建一個 PostgreSQL 數據庫
   - 修改 `plant_diary/database.py` 使用 PostgreSQL
   - 需要安裝 `psycopg2-binary`

2. **使用外部數據庫服務**
   - Supabase（免費 PostgreSQL）
   - ElephantSQL（免費 PostgreSQL）
   - PlanetScale（MySQL）

3. **使用外部存儲服務（照片）**
   - AWS S3
   - Cloudinary（有免費層）
   - Firebase Storage

#### 免費層限制

- 應用在 15 分鐘不活動後會休眠
- 首次訪問需要等待約 30 秒喚醒
- 每月有使用時間限制（750 小時）

---

## 🌐 其他部署選項

### Railway（簡單，推薦）

1. 訪問 https://railway.app
2. 使用 GitHub 登入
3. 選擇 "New Project" → "Deploy from GitHub repo"
4. 選擇您的倉庫
5. 配置環境變數
6. 自動部署

**優點：**
- 免費層可用
- 自動 HTTPS
- 簡單易用

### PythonAnywhere（適合初學者）

1. **註冊帳號**
   - 訪問 https://www.pythonanywhere.com
   - 註冊免費帳號

2. **上傳代碼**
   - 在 Files 標籤中，使用 Git 克隆：
   ```bash
   cd ~
   git clone https://github.com/yourusername/plant_diary.git
   ```

3. **配置 Web App**
   - 進入 Web 標籤
   - 點擊 "Add a new web app"
   - 選擇 Python 3.10 或更高版本
   - 選擇 "Manual configuration"
   - 點擊下一步

4. **配置 WSGI 文件**
   - 點擊 WSGI 配置文件連結
   - 編輯文件，替換為：
   ```python
   import sys
   import os

   path = '/home/yourusername/plant_diary'
   if path not in sys.path:
       sys.path.insert(0, path)

   from plant_diary_web.app import app as application
   ```

5. **安裝依賴**
   - 在 Bash 控制台中：
   ```bash
   pip3.10 install --user -r plant_diary_web/requirements.txt
   ```

6. **設置環境變數**
   - 在 Web 標籤的環境變數部分添加：
   ```
   OPENAI_API_KEY=your-key-here
   SECRET_KEY=your-secret-key-here
   ```

7. **重載應用**
   - 點擊 "Reload" 按鈕

### VPS（完全控制）

如果您有自己的 VPS 或雲伺服器：

**推薦提供商：**
- DigitalOcean ($5/月起)
- Linode ($5/月起)
- Vultr ($5/月起)

**基本部署步驟：**

1. **連接伺服器**
   ```bash
   ssh root@your-server-ip
   ```

2. **安裝依賴**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx git -y
   ```

3. **克隆倉庫**
   ```bash
   cd /var/www
   sudo git clone https://github.com/yourusername/plant_diary.git
   cd plant_diary
   ```

4. **創建虛擬環境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r plant_diary_web/requirements.txt
   pip install gunicorn
   ```

5. **創建 systemd 服務**
   ```bash
   sudo nano /etc/systemd/system/plant-diary.service
   ```
   
   內容：
   ```ini
   [Unit]
   Description=Plant Diary Gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/plant_diary/plant_diary_web
   Environment="PATH=/var/www/plant_diary/venv/bin"
   ExecStart=/var/www/plant_diary/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

   [Install]
   WantedBy=multi-user.target
   ```

6. **啟動服務**
   ```bash
   sudo systemctl start plant-diary
   sudo systemctl enable plant-diary
   ```

7. **配置 Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/plant-diary
   ```
   
   內容：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /uploads {
           alias /var/www/plant_diary/plant_diary_web/plant_photos;
       }
   }
   ```

8. **啟用站點**
   ```bash
   sudo ln -s /etc/nginx/sites-available/plant-diary /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

9. **設置 SSL**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

---

## ✅ 部署前檢查清單

- [ ] 代碼已推送到 GitHub
- [ ] `plant_diary_web/requirements.txt` 包含所有依賴
- [ ] `plant_diary_web/Procfile` 已創建
- [ ] `plant_diary_web/runtime.txt` 指定 Python 版本
- [ ] 已生成 `SECRET_KEY`
- [ ] `OPENAI_API_KEY` 已準備（可選）
- [ ] 已考慮數據持久化方案

---

## 🔍 部署後測試

1. ✅ 訪問應用 URL
2. ✅ 測試註冊功能
3. ✅ 測試登入功能
4. ✅ 測試添加植物
5. ✅ 測試上傳照片
6. ✅ 測試 OCR 識別（如果已設置）

---

## 🆘 常見問題

**Q: 構建失敗怎麼辦？**
- 檢查構建日誌，查看具體錯誤訊息
- 確認 `requirements.txt` 中的版本兼容性
- 確認 Python 版本正確

**Q: 應用啟動後無法訪問？**
- 檢查日誌輸出
- 確認環境變數設置正確
- 檢查端口配置

**Q: 數據會丟失嗎？**
- Render 免費層：會，需要使用外部數據庫
- PythonAnywhere：免費層有備份，但建議定期備份
- VPS：不會，但需要定期備份

**Q: 如何更新應用？**
- 推送新代碼到 GitHub
- Render/Railway 會自動重新部署
- VPS 需要手動執行 `git pull` 和重啟服務

**Q: 上傳的照片存儲在哪裡？**
- 默認在 `plant_diary_web/plant_photos/`
- 在免費雲平台可能不持久，建議使用外部存儲

---

## 📚 相關文件

- `部署指南.md` - 詳細部署文檔
- `plant_diary_web/README.md` - Web 版本說明
- `plant_diary/README.md` - 應用核心說明

祝您部署順利！🌱

