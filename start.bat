@echo off
echo ==========================================
echo   All-to-All File Converter Launcher
echo ==========================================

:: Start Backend
echo Starting Backend (Flask)...
start "All-to-All Backend" cmd /k "cd server && pip install flask flask-cors nbconvert nbformat && python app.py"

:: Start Frontend
echo Starting Frontend (Vite)...
start "All-to-All Frontend" cmd /k "cd client && npm install && npm run dev"

echo Done! Servers are starting in new windows.
echo Waiting for frontend to be ready (this may take a moment if installing dependencies)...

:: Use PowerShell to wait for port 5173 to be active
powershell -Command "while($true) { try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 5173); $c.Dispose(); break } catch { Start-Sleep -Seconds 1 } }"

echo Opening browser...
start http://localhost:5173
pause
