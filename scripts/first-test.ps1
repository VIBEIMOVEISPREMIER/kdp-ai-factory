$ErrorActionPreference="Stop"
Write-Host "=== KDP AI Factory | PRIMEIRO TESTE ===" -ForegroundColor Cyan
if(!(Test-Path ".\.venv\Scripts\python.exe")){ & .\scripts\install.ps1 }
& .\.venv\Scripts\kdp-factory.exe init
Write-Host "Diagnóstico:"
& .\.venv\Scripts\kdp-factory.exe doctor
Write-Host ""
Write-Host "Se o diagnóstico estiver OK, abra outro terminal e execute:" -ForegroundColor Green
Write-Host "  .\scripts\start.ps1"
Write-Host "Depois, em outro terminal:" -ForegroundColor Green
Write-Host "  .\scripts\start-dashboard.ps1"
