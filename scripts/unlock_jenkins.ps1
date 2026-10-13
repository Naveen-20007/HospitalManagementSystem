# CareSync - Unlock Jenkins PowerShell Script
$cfg = "C:\ProgramData\Jenkins\.jenkins\config.xml"
if (Test-Path $cfg) {
    Write-Host "[CareSync] Modifying Jenkins security settings in $cfg..."
    (Get-Content $cfg) -replace '<useSecurity>true</useSecurity>', '<useSecurity>false</useSecurity>' | Set-Content $cfg
    Write-Host "[CareSync] Restarting Jenkins Windows service..."
    Restart-Service Jenkins
    Write-Host "[CareSync] SUCCESS! Jenkins security has been disabled."
    Write-Host "[CareSync] You can now access http://localhost:8080 directly without any login prompt."
    Start-Sleep -Seconds 3
} else {
    Write-Host "[CareSync] ERROR: $cfg not found."
    Start-Sleep -Seconds 5
}
