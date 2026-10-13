@echo off
REM CareSync - Reset Jenkins Security
echo [CareSync] Launching Administrator PowerShell to unlock Jenkins...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0unlock_jenkins.ps1\"'"
echo.
echo [CareSync] If a Windows prompt appears asking "Do you want to allow this app to make changes", click YES.
echo [CareSync] Once done, refresh http://localhost:8080 in your browser!
pause
