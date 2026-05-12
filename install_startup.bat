@echo off
REM Script nay se them HTQL NhanSu vao Windows Startup
REM Chay file nay 1 lan de cai dat tu dong khoi dong

set "SOURCE=%~dp0run.bat"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\HTQL_NhanSu.bat"

echo ============================================
echo   CAI DAT TU DONG KHOI DONG
echo ============================================
echo.
echo Dang tao shortcut trong thu muc Startup...

copy "%SOURCE%" "%SHORTCUT%" >nul

if exist "%SHORTCUT%" (
    echo [THANH CONG] Da them vao Startup!
    echo.
    echo Tu nay moi lan bat may, web se tu dong chay.
    echo Truy cap tai: http://127.0.0.1:5000
    echo.
    echo De go cai dat, chay file: remove_startup.bat
) else (
    echo [LOI] Khong tao duoc shortcut. Chay lai voi quyen Admin.
)

echo.
pause
