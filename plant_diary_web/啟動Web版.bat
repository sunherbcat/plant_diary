@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 檢查是否設置了 OpenAI API 密鑰
if "%OPENAI_API_KEY%"=="" (
    echo ========================================
    echo   未檢測到 OpenAI API 密鑰
    echo ========================================
    echo.
    echo 要使用 AI 分析功能，請先設置 OpenAI API 密鑰。
    echo.
    echo 方法 1（推薦）：運行「設置OpenAI_API密鑰.bat」進行永久設置
    echo 方法 2：在 PowerShell 中臨時設置：
    echo    $env:OPENAI_API_KEY="your-api-key-here"
    echo.
    echo 繼續啟動應用程式（AI 分析功能將不可用）...
    echo.
    timeout /t 3 /nobreak >nul
)

echo 正在啟動植物日記 Web 版...
echo.
echo 服務器啟動後，您可以：
echo 1. 在電腦瀏覽器中訪問: http://localhost:5000
echo 2. 在手機瀏覽器中訪問: http://你的電腦IP:5000
echo.
echo 按 Ctrl+C 停止服務器
echo.
python app.py
pause


