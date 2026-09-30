$ErrorActionPreference = "Stop"
Write-Host "KDP AI Factory - iniciando ambiente Docker..." -ForegroundColor Cyan
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "Falha ao iniciar o Docker Compose." }
Write-Host ""
Write-Host "Factory iniciado." -ForegroundColor Green
Write-Host "Dashboard: http://localhost:8080" -ForegroundColor Yellow
Write-Host "Logs:      docker compose logs -f" -ForegroundColor Yellow
