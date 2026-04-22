from fastapi import FastAPI, HTTPException
import redis
import uuid
import os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

r = redis.Redis(REDIS_HOST, REDIS_PORT)


def get_redis_client():
    return r


@app.get("/health")
def health():
    try:
        r.ping()
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    return {"status": "ok"}


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        # add http error code
        raise HTTPException(status_code=404, detail={"error": "Job not found"})
    return {"job_id": job_id, "status": status.decode()}
