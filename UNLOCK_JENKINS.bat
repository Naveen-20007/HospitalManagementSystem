@echo off
:: ==============================================================================
:: CareSync - One-Click Jenkins Password Unlocker
:: ==============================================================================
echo ==============================================================================
echo          CareSync - Resetting Jenkins Password & Security
echo ==============================================================================
echo.

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges!
    goto :RESET_JENKINS
) else (
    echo [!] Requesting Administrator privileges to reset Jenkins configuration...
    echo [!] Please click "YES" on the Windows prompt on your screen!
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

:RESET_JENKINS
echo [1/3] Disabling password security in Jenkins config.xml...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$cfg = 'C:\ProgramData\Jenkins\.jenkins\config.xml'; if (Test-Path $cfg) { (Get-Content $cfg) -replace '<useSecurity>true</useSecurity>', '<useSecurity>false</useSecurity>' | Set-Content $cfg; Write-Host '  -> Password security disabled successfully!' } else { Write-Host '  -> Config not found at standard path.' }"

echo [2/3] Restarting Jenkins Windows Service...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Restart-Service Jenkins"

echo [3/3] DONE! Jenkins is now unlocked.
echo.
echo ==============================================================================
echo  SUCCESS: You can now open http://localhost:8080 in your browser.
echo  Jenkins will open directly with FULL ADMIN ACCESS and NO PASSWORD!
echo ==============================================================================
echo.
pause
