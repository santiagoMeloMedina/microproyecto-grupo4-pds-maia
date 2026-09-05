#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

if command -v apt-get >/dev/null 2>&1; then
	sudo apt update
	sudo apt install -y make python3-pip python3-venv
	sudo apt-get install -y libgomp1
fi

if [ ! -d "$VENV_DIR" ]; then
	python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install "dvc[s3]"
pip install -r exploration/requirements.txt
pip install -r models/requirements.txt
