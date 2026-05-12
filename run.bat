@echo off
title HTQL Nhan Su - Web Server
color 0A

echo ============================================
echo    HE THONG QUAN LY NHAN SU
echo    Dang khoi dong web server...
echo ============================================
echo.

cd /d "%~dp0"

echo [OK] Thu muc: %~dp0
echo [OK] Kiem tra Python...

if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Khong tim thay .venv! Vui long chay: python -m venv .venv
    pause
    exit /b 1
)

echo [OK] Dang khoi dong Flask...
echo.
echo  - Truy cap web tai: http://127.0.0.1:5000
echo  - Nhan CTRL+C de dung server
echo.
echo ============================================

.venv\Scripts\python.exe app.py

pause
