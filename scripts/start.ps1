$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Ambiente não instalado. Execute: .\scripts\install.ps1" -ForegroundColor Yellow
    exit 1
}

& .\.venv\Scripts\kdp-factory.exe init
& .\.venv\Scripts\kdp-factory.exe start
