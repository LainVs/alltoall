@echo off
echo ==========================================
echo   All-to-All File Converter Launcher
echo ==========================================

echo [1/3] Checking and installing backend dependencies...
cd server
pip install -r requirements.txt
cd ..

echo.
echo [2/3] Checking and installing frontend dependencies...
cd client
call npm install
cd ..

echo.
echo [3/3] Starting Unified Runner...
:: Start Unified Runner
python run.py

pause
