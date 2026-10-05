import uuid
import json
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Async Job Queue Engine")
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, protocol=2)

QUEUE_NAME = "task_queue"

class JobRequest(BaseModel):
    task_type: str
    payload: dict
    should_fail: bool = False  # Retry mekanizmasını test.

@app.post("/jobs", status_code=202)
def submit_job(request: JobRequest):
    job_id = str(uuid.uuid4())
    
    job_data = {
        "job_id": job_id,
        "task_type": request.task_type,
        "payload": request.payload,
        "should_fail": request.should_fail,
        "attempts": 0
    }
    
    #İş durumu redis hash kaydtme
    r.hset(f"job:{job_id}", mapping={
        "status": "QUEUED",
        "attempts": 0,
        "task_type": request.task_type
    })
    
    #İşi kuyruğa eklendi
    r.lpush(QUEUE_NAME, json.dumps(job_data))
    
    return {
        "job_id": job_id,
        "status": "QUEUED",
        "message": "İş kuyruğa eklendi"
    }

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job_data = r.hgetall(f"job:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="İş bulunamadı")
    return job_data