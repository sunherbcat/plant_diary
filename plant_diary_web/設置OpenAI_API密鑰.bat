@echo off
chcp 65001 >nul
echo ========================================
echo   設置 OpenAI API 密鑰（永久設置）
echo ========================================
echo.
echo 請輸入您的 OpenAI API 密鑰：
echo （輸入後按 Enter，密鑰將被永久保存到系統環境變數）
echo.

set /p API_KEY="API 密鑰: "

if "%API_KEY%"=="" (
    echo.
    echo 錯誤：未輸入密鑰
    pause
    exit /b 1
)

echo.
echo 正在設置環境變數...

:: 使用 setx 命令永久設置用戶級別的環境變數
setx OPENAI_API_KEY "%API_KEY%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   設置成功！
    echo ========================================
    echo.
    echo OpenAI API 密鑰已永久保存到系統環境變數。
    echo.
    echo 注意：您需要重新啟動 PowerShell 或命令提示符窗口，
    echo       環境變數才會生效。或者您可以：
    echo   1. 關閉當前所有 PowerShell/CMD 窗口
    echo   2. 重新打開 PowerShell/CMD
    echo   3. 運行「啟動Web版.bat」
    echo.
) else (
    echo.
    echo 設置失敗，請以管理員權限運行此腳本。
    echo.
)

pause



