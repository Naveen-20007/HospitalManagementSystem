Write-Host "=== 1. GIT BASELINE ==="
git status
git remote -v
git log -3 --oneline

Write-Host "`n=== 2. CONTAINER BASELINE ==="
docker compose ps

Write-Host "`n=== 3. HEALTH BASELINE ==="
try {
    $res = Invoke-RestMethod -Uri "http://localhost:8081/health" -Method Get
    Write-Host "Health:" ($res | ConvertTo-Json -Compress)
} catch {
    Write-Host "Health check failed: $_"
}

Write-Host "`n=== 4. PYTEST BASELINE ==="
.\.venv\Scripts\pytest.exe -q

Write-Host "`n=== 5. JENKINS BASELINE ==="
Get-Service Jenkins | Select-Object Name, Status, StartType | Format-Table -AutoSize
try {
    $j = Invoke-RestMethod -Uri "http://localhost:8080/job/CareSync-Complete-CICD/api/json" -Method Get
    Write-Host "Job: $($j.name), LastBuild: #$($j.lastBuild.number), LastSuccessfulBuild: #$($j.lastSuccessfulBuild.number)"
} catch {
    Write-Host "Jenkins query: $_"
}
