import os
import uuid

import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

r = redis.Redis(REDIS_HOST, REDIS_PORT)


@app.get("/health")
def health():
    try:
        r.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return JSONResponse({"status": "ok"})


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return JSONResponse({"job_id": job_id})


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail={"error": "Job not found"})
    return JSONResponse({"job_id": job_id, "status": status.decode()})
