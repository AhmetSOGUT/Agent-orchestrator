import uuid
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from orchestrator import run_research_pipeline
from config import settings
from logging_config import setup_logging, get_logger
from job_store import job_store, JobStatus

setup_logging(level=settings.log_level)
logger = get_logger(__name__)

app = FastAPI(title="AI Research Orchestrator")

class ResearchRequest(BaseModel):
    topic: str


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus


async def _run_job(job_id: str, topic: str):
    logger.info(f"Job başladı: {job_id} - konu: '{topic}'")
    await job_store.update(job_id, status=JobStatus.RUNNING)
    try:
        result = await run_research_pipeline(topic)
        await job_store.update(job_id, status=JobStatus.DONE, result=result)
        logger.info(f"Job tamamlandı: {job_id}")
    except Exception as e:
        await job_store.update(job_id, status=JobStatus.FAILED, error=str(e))
        logger.error(f"Job başarısız: {job_id} - hata: {e}", exc_info=True)


@app.post("/research", response_model=JobResponse)
async def start_research(request: ResearchRequest):
    job_id = str(uuid.uuid4())
    await job_store.create(job_id)
    logger.info(f"Yeni research isteği alındı: {job_id}")

    asyncio.create_task(_run_job(job_id, request.topic))

    return JobResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/research/{job_id}")
async def get_research_status(job_id: str):
    job = await job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    return job


@app.get("/health")
async def health_check():
    """Sağlık kontrolü - deployment/monitoring sistemleri için standart endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "AI Research Orchestrator çalışıyor."}