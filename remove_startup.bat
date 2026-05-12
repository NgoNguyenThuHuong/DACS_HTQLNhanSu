@echo off
title Go cai dat Startup

set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\HTQL_NhanSu.bat"

echo ============================================
echo   GO CAI DAT TU DONG KHOI DONG
echo ============================================
echo.

if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo [THANH CONG] Da xoa khoi Startup!
    echo Web se KHONG tu dong chay nua khi bat may.
) else (
    echo [THONG BAO] Chua duoc cai dat trong Startup.
)

echo.
pause
