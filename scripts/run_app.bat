@echo off
REM CareSync - Run Flask Development Server on Windows
echo [CareSync] Starting application...
cd /d "%~dp0\.."

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

python -c "import app" 2>nul || (
    echo [CareSync] Installing requirements...
    pip install -r requirements.txt
)

REM Initialize / seed database if not found
if not exist "caresync.db" (
    echo [CareSync] Initializing and seeding database...
    python scripts\seed_data.py
)

echo [CareSync] Server running at http://localhost:5000
echo Default credentials:
echo   Administrator: admin / admin123
echo   Doctor:        dr.sarah / doctor123
echo   Patient:       john_doe / patient123
echo.
python app.py
pause
