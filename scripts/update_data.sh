#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
	./scripts/install.sh
fi

source "$VENV_DIR/bin/activate"

if ! command -v dvc >/dev/null 2>&1; then
	./scripts/install.sh
	source "$VENV_DIR/bin/activate"
fi

DATA_DIR="data"

files=()
while IFS= read -r -d '' file; do
	files+=("$file")
done < <(find "$DATA_DIR" -maxdepth 1 -type f ! -name "*.dvc" ! -name ".gitignore" -print0)

if [ ${#files[@]} -eq 0 ]; then
	echo "No hay archivos en $DATA_DIR/ para versionar."
	exit 0
fi

versioned=()
for file in "${files[@]}"; do
	read -r -p "¿Versionar '$file' con DVC? [y/N] " answer
	if [[ "$answer" =~ ^[Yy]$ ]]; then
		dvc add "$file"
		versioned+=("$file")
	fi
done

if [ ${#versioned[@]} -eq 0 ]; then
	echo "No se versionó ningún archivo."
	exit 0
fi

echo "Archivos versionados:"
printf '  %s\n' "${versioned[@]}"

read -r -p "¿Hacer 'dvc push' de los archivos versionados? [y/N] " push_answer
if [[ "$push_answer" =~ ^[Yy]$ ]]; then
	dvc push
fi
