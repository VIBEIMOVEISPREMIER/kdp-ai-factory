$ErrorActionPreference = "Stop"

Write-Host "=== KDP AI Factory - instalação ===" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python 3.11+ não encontrado. Instale Python e marque 'Add Python to PATH'." -ForegroundColor Red
    exit 1
}

python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Instalação concluída." -ForegroundColor Green
Write-Host "Próximo passo: .\.venv\Scripts\kdp-factory.exe doctor"
