# Makefile para Windows.
#
# El Makefile de la raiz delega en scripts/install.sh y scripts/update_data.sh,
# que estan escritos para macOS y Linux. Este archivo ofrece los mismos targets
# apoyandose en los scripts de PowerShell de esta carpeta, para quien tenga GNU
# Make instalado en Windows y prefiera mantener el mismo flujo de comandos.
#
# Uso, desde la raiz del repositorio:
#
#     make -f scripts/windows/Makefile install
#     make -f scripts/windows/Makefile update-data
#
# Requiere GNU Make en Windows (por ejemplo `scoop install make`,
# `choco install make` o `winget install GnuWin32.Make`). Si no esta instalado,
# los scripts .ps1 se pueden invocar directamente; ver README.md de esta carpeta.

.PHONY: install update-data help

POWERSHELL := powershell -NoProfile -ExecutionPolicy Bypass -File

help:
	@echo Targets disponibles: install, update-data
	@echo Ejecutar desde la raiz del repositorio con: make -f scripts/windows/Makefile ^<target^>

install:
	$(POWERSHELL) scripts/windows/install.ps1

update-data:
	$(POWERSHELL) scripts/windows/update_data.ps1
