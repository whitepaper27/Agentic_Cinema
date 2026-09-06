# StudioClear — Cloud Run image (sol.md E3.2 / E3.4).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY studioclear/ ./studioclear/
COPY app/ ./app/
COPY demo/ ./demo/

# Cloud Run provides $PORT. On Cloud Run, PARALLEL_API_KEY / GEMINI_API_KEY are
# injected from Secret Manager via the service account (see deploy/terraform).
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT}"]
