@echo off
title CareSync - Automatic Jenkins CI/CD Build ^& Launch
color 0A
echo ==============================================================================
echo       CareSync: Automatic Jenkins Pipeline Build ^& Website Launcher
echo ==============================================================================
echo.
echo [1/3] Triggering Jenkins CI/CD pipeline build...
echo [2/3] Running tests, building Docker image, and deploying containers...
echo.

cd /d "%~dp0"
call .\.venv\Scripts\activate.bat
python -u scripts\run_caresync_pipeline.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==============================================================================
    echo [SUCCESS] Build completed! Opening CareSync in your default browser...
    echo ==============================================================================
    start http://localhost:8081
) else (
    echo.
    echo ==============================================================================
    echo [FAILED] Pipeline encountered errors. Please check the logs above.
    echo ==============================================================================
)

echo.
pause
