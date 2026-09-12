# Imagen de la API de riesgo de retraso.
#
# Se construye desde la raiz del repositorio porque necesita api/ y el
# historico de dashboard/data/:
#
#   docker build -f api/Dockerfile -t airlines-api .
#   docker run -p 8002:8002 airlines-api
#
# El modelo no se copia como archivo suelto ni se deserializa a mano: se
# instala desde el wheel de api/model-package/, que ya trae el pipeline
# entrenado y fija las versiones de scikit-learn y xgboost con las que se
# entreno.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/api

# libgomp1 lo necesita XGBoost para su paralelismo con OpenMP. Sin ella, el
# import falla con un error de biblioteca compartida que no menciona a XGBoost.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Las dependencias van antes que el codigo para aprovechar la cache de capas:
# cambiar un endpoint no deberia obligar a reinstalar xgboost.
COPY api/requirements.txt ./requirements.txt
COPY api/model-package ./model-package
RUN pip install --no-cache-dir -r requirements.txt

COPY api/app ./app
COPY dashboard/data/vuelos.parquet /app/dashboard/data/vuelos.parquet

ENV AIRLINES_PARQUET=/app/dashboard/data/vuelos.parquet

# Usuario sin privilegios: nada de lo que hace la API necesita root.
RUN useradd --create-home --uid 1000 api && chown -R api:api /app
USER api

EXPOSE 8002

# start-period generoso: al primer arranque la API puntua las 92.250 franjas
# del itinerario con el modelo, y eso toma varios segundos.
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8002/api/v1/health', timeout=8).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
