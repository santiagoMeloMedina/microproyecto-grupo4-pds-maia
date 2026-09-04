# Equivalente en Windows de scripts/install.sh
#
# install.sh usa `source .venv/bin/activate`, una ruta que solo existe cuando el
# entorno virtual se crea en macOS o Linux. En Windows `python -m venv` genera
# `.venv\Scripts\`, por lo que ese script falla. Este archivo hace exactamente lo
# mismo pero con las rutas de Windows, sin modificar el script original.
#
# Uso, desde cualquier ubicacion:
#   powershell -ExecutionPolicy Bypass -File scripts\windows\install.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

function Get-BasePython {
    # El lanzador `py` es la forma recomendada en Windows; `python` puede apuntar
    # al alias de la Microsoft Store, que no sirve para crear entornos virtuales.
    $launcher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($null -ne $launcher) {
        return @{ Exe = $launcher.Source; Args = @("-3") }
    }

    $python = Get-Command "python" -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        return @{ Exe = $python.Source; Args = @() }
    }

    throw "No se encontro Python. Instalalo desde https://www.python.org/downloads/ y marca 'Add python.exe to PATH'."
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creando entorno virtual en $VenvDir ..."
    $base = Get-BasePython
    & $base.Exe @($base.Args + @("-m", "venv", $VenvDir))
    if ($LASTEXITCODE -ne 0) { throw "Fallo la creacion del entorno virtual." }
}
else {
    Write-Host "El entorno virtual ya existe en $VenvDir, se reutiliza."
}

Write-Host "Actualizando pip ..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Fallo la actualizacion de pip." }

Write-Host "Instalando dvc[s3] ..."
& $VenvPython -m pip install "dvc[s3]"
if ($LASTEXITCODE -ne 0) { throw "Fallo la instalacion de dvc[s3]." }

$Requirements = Join-Path $RepoRoot "exploration\requirements.txt"
Write-Host "Instalando dependencias de exploration/requirements.txt ..."
& $VenvPython -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) { throw "Fallo la instalacion de exploration/requirements.txt." }

Write-Host ""
Write-Host "Listo. Para activar el entorno en esta terminal:"
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host "Para salir del entorno: deactivate"
