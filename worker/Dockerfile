FROM python:3.12-slim AS builder

WORKDIR /worker

COPY requirements.txt /worker/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=30s --start-period=15s --retries=3 \
    CMD python -c import redis, os r=redis.Redis(host=os.getenv('REDIS_HOST'), \
        port=os.getenv('REDIS_PORT'), password=os.getenv('REDIS_PASSWORD')) r.ping()

RUN useradd app

USER app


CMD ["python", "worker.py"]
