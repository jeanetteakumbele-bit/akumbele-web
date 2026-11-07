# Construye la web y la abre en el navegador para revisarla antes de publicar.
# Uso:  clic derecho > "Ejecutar con PowerShell"   o   .\ver-en-local.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python construir.py
if ($LASTEXITCODE -ne 0) { Write-Host "Ha fallado la construcción." -ForegroundColor Red; Read-Host "Pulsa Enter"; exit 1 }

$puerto = 8000
Write-Host ""
Write-Host "Abriendo http://localhost:$puerto  (cierra esta ventana para pararlo)" -ForegroundColor Green
Start-Process "http://localhost:$puerto"
python -m http.server $puerto --directory _site
