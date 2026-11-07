# Publica los cambios en GitHub. GitHub reconstruye la web sola en 1-2 minutos.
# Uso:  .\publicar.ps1                      (mensaje automático)
#       .\publicar.ps1 "Nueva historia"     (con tu mensaje)
param([string]$Mensaje = "")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 1. Comprobar que la web se construye bien antes de subir nada
python construir.py
if ($LASTEXITCODE -ne 0) { Write-Host "La web tiene un error; no se publica." -ForegroundColor Red; exit 1 }

# 2. ¿Hay cambios?
$cambios = git status --porcelain
if (-not $cambios) { Write-Host "No hay cambios que publicar." -ForegroundColor Yellow; exit 0 }
git status --short

# 3. Guardar y subir
if (-not $Mensaje) { $Mensaje = "Actualizar web " + (Get-Date -Format "yyyy-MM-dd HH:mm") }
git add -A
git commit -m $Mensaje
git push
if ($LASTEXITCODE -ne 0) { Write-Host "No se ha podido subir a GitHub." -ForegroundColor Red; exit 1 }

$url = gh repo view --json homepageUrl -q .homepageUrl 2>$null
Write-Host ""
Write-Host "Publicado. En 1-2 minutos estará en: $url" -ForegroundColor Green
