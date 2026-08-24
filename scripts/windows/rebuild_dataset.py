"""SOLO PARA TEST: Reconstruye data/airlines.csv desde el ARFF original de OpenML.

El CSV versionado con DVC es exactamente la seccion @data del ARFF publico de
OpenML (dataset id 1169) con la fila de encabezado antepuesta, sin ninguna otra
transformacion. Reconstruirlo asi produce un archivo identico byte a byte al que
apunta data/airlines.csv.dvc, por lo que sirve para trabajar sin credenciales de
AWS: DVC lo reconoce como valido.

Uso:
    python scripts/windows/rebuild_dataset.py <ruta_al_arff> <ruta_csv_destino>

El ARFF se descarga de:
    https://openml.org/data/v1/download/66526/airlines.arff

Aunque vive en scripts/windows/ por conveniencia, no depende del sistema
operativo: funciona igual en macOS y Linux.
"""
import hashlib
import sys

HEADER = b"Airline,Flight,AirportFrom,AirportTo,DayOfWeek,Time,Length,Delay\n"
MARKER = b"@" + b"data" + b"\n"
MD5_ESPERADO = "9912b30b4059e7bfdc58eb5b5a1ca043"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1

    arff_path, csv_path = sys.argv[1], sys.argv[2]

    with open(arff_path, "rb") as fh:
        raw = fh.read()

    inicio = raw.find(MARKER)
    if inicio == -1:
        print("Error: no se encontro la seccion de datos en el ARFF.")
        return 1

    cuerpo = raw[inicio + len(MARKER):]
    contenido = HEADER + cuerpo

    with open(csv_path, "wb") as fh:
        fh.write(contenido)

    digest = hashlib.md5(contenido).hexdigest()
    print(f"Escrito : {csv_path} ({len(contenido):,} bytes)")
    print(f"MD5     : {digest}")

    if digest == MD5_ESPERADO:
        print("El archivo coincide con el versionado en data/airlines.csv.dvc.")
        print("Siguiente paso: dvc commit data/airlines.csv.dvc --force")
        return 0

    print(f"ATENCION: se esperaba {MD5_ESPERADO}.")
    print("El ARFF de origen pudo haber cambiado. Revisa antes de usar los datos.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
