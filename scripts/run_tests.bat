@echo off
REM CareSync - Run Automated Pytest Suite and Generate JUnit XML Report for Jenkins
echo [CareSync] Running automated test suite...
cd /d "%~dp0\.."

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

if not exist "reports" (
    mkdir reports
)

pytest -v --junitxml=reports/junit.xml
echo.
echo [CareSync] Test execution finished. Exit code: %ERRORLEVEL%
exit /b %ERRORLEVEL%
