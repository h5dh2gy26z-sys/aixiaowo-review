$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

python -m pip install -r requirements.txt | Out-Host

# Ensure frontend dist exists (so opening http://127.0.0.1:8731 shows UI)
$distIndex = Join-Path $PSScriptRoot "..\\frontend\\dist\\index.html"
if (-Not (Test-Path $distIndex)) {
  Write-Host "Frontend dist missing. Building..." -ForegroundColor Yellow
  Push-Location (Join-Path $PSScriptRoot "..\\frontend")
  try {
    npm install | Out-Host
    npm run build | Out-Host
  } finally {
    Pop-Location
  }
}

python -m uvicorn app.main:app --host 127.0.0.1 --port 8731
