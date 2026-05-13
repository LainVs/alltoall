@echo off
chcp 65001 >nul 2>&1
title All-to-All First Install
echo Installing backend dependencies...
pip install -r "%~dp0server\requirements.txt"
if %errorlevel% neq 0 (
    echo Backend install failed!
    pause
    exit /b 1
)
echo Backend OK
echo.
echo Installing frontend dependencies...
cd /d "%~dp0client"
call npm install
if %errorlevel% neq 0 (
    echo Frontend install failed!
    pause
    exit /b 1
)
echo Frontend OK
echo.
echo ==========================================
echo   Install complete! Run start.bat to launch.
echo ==========================================
echo.
echo Optional: pip install -r server\requirements-optional.txt
echo.
pause
