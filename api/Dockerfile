# Build desde la raiz del repo (necesita api/, models/ y dashboard/data/):
#   docker build -f api/Dockerfile -t airlines-api .
#   docker run -p 8002:8002 airlines-api
#
# api/app/services/artifacts.py resuelve ROOT como parents[3] de si mismo, por
# eso la imagen preserva la misma estructura relativa que el repo (api/,
# models/, dashboard/data/, airlines_ml/) en vez de aplanarla. airlines_ml/ es
# necesario porque el .joblib fue serializado con sus clases (transformers de
# features.py); sin el paquete en sys.path, joblib.load falla con
# ModuleNotFoundError al deserializar.
FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

COPY api/app api/app
COPY models models
COPY dashboard/data dashboard/data
COPY airlines_ml airlines_ml

WORKDIR /app/api

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
