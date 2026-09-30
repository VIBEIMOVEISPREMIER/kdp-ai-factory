$ErrorActionPreference="Stop"
if (-not (Test-Path ".\apps\dashboard\node_modules")) { Push-Location ".\apps\dashboard"; npm install; Pop-Location }
Push-Location ".\apps\dashboard"
npm run dev
Pop-Location
