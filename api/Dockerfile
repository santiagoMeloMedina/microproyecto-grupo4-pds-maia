# Build desde la raiz del repo (necesita api/, models/ y dashboard/data/):
#   docker build -f api/Dockerfile -t airlines-api .
#   docker run -p 8002:8002 airlines-api
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
