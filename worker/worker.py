import os
import time

import redis

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

r = redis.Redis(REDIS_HOST, REDIS_PORT)

print(f"Worker starting. Redis={REDIS_HOST}:{REDIS_PORT}", flush=True)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


def main():
    while True:
        job = r.brpop("job", timeout=5)
        if job:
            _, job_id = job
            try:
                process_job(job_id.decode())
            except Exception as exc:
                print(f"ERROR processing job {job_id}: {exc}", flush=True)
                try:
                    r.hset(f"job:{job_id}", "status", "failed")
                except Exception:
                    pass


if __name__ == "__main__":
    main()
