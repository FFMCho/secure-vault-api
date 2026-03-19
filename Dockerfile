FROM python:3.12-slim

WORKDIR /app

# curl für Healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/
COPY scripts/entrypoint.py /entrypoint.py

EXPOSE 8000

ENTRYPOINT ["python", "/entrypoint.py"]
