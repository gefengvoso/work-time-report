@echo off
cd /d "%~dp0"

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Starting Work Hours app at http://localhost:5001
echo Press Ctrl+C to stop.
echo.

start "" python app.py

:waitloop
timeout /t 1 /nobreak >nul
curl -s http://localhost:5001/ >nul 2>&1
if errorlevel 1 goto waitloop

start "" "http://localhost:5001"

echo Server is running.
echo To expose it via Cloudflare Tunnel, run cloudflared-tunnel.bat in a separate window.
pause >nul
