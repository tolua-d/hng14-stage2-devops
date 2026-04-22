FROM python:3.11-slim AS builder

WORKDIR /code

COPY requirements.txt /code/

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl=7.68.0-1ubuntu2.25 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && useradd app   

USER app

COPY main.py .

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3\
 CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]