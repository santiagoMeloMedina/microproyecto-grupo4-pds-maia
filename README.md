# Microproyecto

## Instalación

Requisitos: Python 3.

```bash
make install
```

Esto crea un entorno virtual en `.venv/` e instala `dvc[s3]` dentro de él.

`make install` no deja el entorno activado en tu shell. Para poder usar los comandos instalados (por ejemplo `dvc`), actívalo manualmente después:

```bash
source .venv/bin/activate
```

Repite este `source .venv/bin/activate` cada vez que abras una terminal nueva y quieras seguir usando el proyecto. Para salir del entorno virtual: `deactivate`.
