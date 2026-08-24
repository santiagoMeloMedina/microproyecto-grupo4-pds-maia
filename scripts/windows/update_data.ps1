# Equivalente en Windows de scripts/update_data.sh
#
# Recorre los archivos de data/, pregunta uno por uno si versionarlos con DVC y
# al final ofrece hacer `dvc push`. Mismo comportamiento que el script original;
# solo cambian las rutas del entorno virtual, que en Windows viven en
# `.venv\Scripts\` y no en `.venv/bin/`.
#
# Uso, desde cualquier ubicacion:
#   powershell -ExecutionPolicy Bypass -File scripts\windows\update_data.ps1
#
# Parametros opcionales:
#   -Remote <nombre>   Empuja a un remote concreto (por ejemplo el remote local
#                      propio configurado con `dvc remote add --local`).

param(
    [string]$Remote = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$DataDir = Join-Path $RepoRoot "data"

if (-not (Test-Path $VenvPython)) {
    Write-Host "No existe el entorno virtual. Ejecutando scripts\windows\install.ps1 ..."
    & (Join-Path $PSScriptRoot "install.ps1")
}

# Se invoca DVC como modulo del interprete del entorno virtual para no depender
# de que el entorno este activado en la terminal actual.
& $VenvPython -m dvc --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "DVC no esta disponible en el entorno. Reinstalando ..."
    & (Join-Path $PSScriptRoot "install.ps1")
}

$files = Get-ChildItem -Path $DataDir -File |
    Where-Object { $_.Extension -ne ".dvc" -and $_.Name -ne ".gitignore" }

if ($files.Count -eq 0) {
    Write-Host "No hay archivos en data/ para versionar."
    exit 0
}

$versioned = @()
foreach ($file in $files) {
    $relative = "data/" + $file.Name
    $answer = Read-Host "Versionar '$relative' con DVC? [y/N]"
    if ($answer -match '^[Yy]$') {
        Push-Location $RepoRoot
        try {
            & $VenvPython -m dvc add $relative
            if ($LASTEXITCODE -ne 0) { throw "Fallo 'dvc add $relative'." }
        }
        finally {
            Pop-Location
        }
        $versioned += $relative
    }
}

if ($versioned.Count -eq 0) {
    Write-Host "No se versiono ningun archivo."
    exit 0
}

Write-Host "Archivos versionados:"
foreach ($item in $versioned) { Write-Host "  $item" }

$pushAnswer = Read-Host "Hacer 'dvc push' de los archivos versionados? [y/N]"
if ($pushAnswer -match '^[Yy]$') {
    Push-Location $RepoRoot
    try {
        if ([string]::IsNullOrWhiteSpace($Remote)) {
            & $VenvPython -m dvc push
        }
        else {
            & $VenvPython -m dvc push --remote $Remote
        }
        if ($LASTEXITCODE -ne 0) { throw "Fallo 'dvc push'. Revisa tus credenciales de AWS." }
    }
    finally {
        Pop-Location
    }
}
