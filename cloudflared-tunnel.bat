@echo off
cd /d "%~dp0"

REM Check for cloudflared in local dir or PATH
if exist "%~dp0cloudflared.exe" (
    set CF="%~dp0cloudflared.exe"
    goto :run
)
where cloudflared >nul 2>&1
if not errorlevel 1 (
    set CF=cloudflared
    goto :run
)

echo cloudflared.exe not found.
echo Download it from: https://github.com/cloudflare/cloudflared/releases/latest
echo Save cloudflared-windows-amd64.exe as cloudflared.exe in this folder, then re-run.
pause
exit /b 1

:run
echo.
echo Starting Cloudflare Tunnel → http://localhost:5001
echo Your public URL will appear below (look for trycloudflare.com or your domain).
echo Press Ctrl+C to stop.
echo.
%CF% tunnel --url http://localhost:5001
