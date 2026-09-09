import uuid
import asyncio
from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from orchestrator import run_research_pipeline
from config import settings
from logging_config import setup_logging, get_logger

setup_logging(level=settings.log_level)
logger = get_logger(__name__)

app = FastAPI(title="AI Research Orchestrator")

# ---- In-memory job store ----
# job_id -> { "status": ..., "result": ... }
jobs: dict[str, dict] = {}


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    topic: str


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus


# ---- Arka planda çalışacak asıl iş ----
async def _run_job(job_id: str, topic: str):
    logger.info(f"Job başladı: {job_id} - konu: '{topic}'")
    jobs[job_id]["status"] = JobStatus.RUNNING
    try:
        result = await run_research_pipeline(topic)
        jobs[job_id]["status"] = JobStatus.DONE
        jobs[job_id]["result"] = result
        logger.info(f"Job tamamlandı: {job_id}")
    except Exception as e:
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
        logger.error(f"Job başarısız: {job_id} - hata: {e}", exc_info=True)



@app.post("/research", response_model=JobResponse)
async def start_research(request: ResearchRequest):
    """
    Yeni bir araştırma job'ı başlatır, hemen job_id döner.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": JobStatus.PENDING, "result": None}
    logger.info(f"Yeni research isteği alındı: {job_id}")

    # asyncio.create_task: işi arka planda başlatır, endpoint'i BEKLETMEZ
    asyncio.create_task(_run_job(job_id, request.topic))

    return JobResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/research/{job_id}")
async def get_research_status(job_id: str):
    """
    Job'ın durumunu ve (bitmişse) sonucunu döner.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job bulunamadı")

    return jobs[job_id]


@app.get("/")
async def root():
    return {"message": "AI Research Orchestrator çalışıyor."}