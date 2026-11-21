import os
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import SessionLocal
from backend.app.models.job import Job
from backend.app.models.resume import Resume
from backend.app.services.resume_parser import parse_resume_file
from backend.app.services.matching_service import match_resume_to_job

# ThreadPoolExecutor for asynchronous background execution when Celery worker is optional
_executor = ThreadPoolExecutor(max_workers=4)

def process_single_resume_pipeline(resume_id: str):
    """
    Core pipeline to parse an uploaded resume, extract metadata, and run AI matching.
    Handles corrupt, empty, and scanned files gracefully without affecting other files.
    """
    db: Session = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            logger.error(f"Resume with ID {resume_id} not found.")
            return
            
        logger.info(f"Starting processing for resume: {resume.filename} (ID: {resume.id})")
        resume.status = "parsing"
        db.commit()
        
        # 1. Parse File
        parse_result = parse_resume_file(resume.file_path, resume.filename)
        if not parse_result["success"]:
            resume.status = "failed"
            resume.error_message = parse_result["error_message"]
            db.commit()
            logger.warning(f"Resume {resume.filename} parsing failed: {parse_result['error_message']}")
            return
            
        resume.raw_text = parse_result["text"]
        resume.parsed_metadata = {
            "candidate_name": parse_result["candidate_name"],
            "email": parse_result["email"],
            "phone": parse_result["phone"]
        }
        resume.status = "matching"
        db.commit()
        
        # 2. Run AI Matching against the target Job
        job = db.query(Job).filter(Job.id == resume.job_id).first()
        if not job:
            resume.status = "failed"
            resume.error_message = "Associated job position not found."
            db.commit()
            return
            
        match_resume_to_job(db, job, resume)
        logger.info(f"Completed processing for resume: {resume.filename}")
        
    except Exception as e:
        logger.error(f"Unexpected error processing resume {resume_id}: {str(e)}", exc_info=True)
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.status = "failed"
                resume.error_message = f"Processing error: {str(e)}"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()

# Celery Task Definition (for production cluster deployment)
try:
    from celery import Celery
    celery_app = Celery(
        "talentmatch_tasks",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND
    )
    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )

    @celery_app.task(bind=True, max_retries=3)
    def celery_process_resume(self, resume_id: str):
        try:
            process_single_resume_pipeline(resume_id)
        except Exception as exc:
            logger.error(f"Celery task error on {resume_id}, retrying: {exc}")
            raise self.retry(exc=exc, countdown=5)
except Exception as e:
    celery_app = None

def dispatch_resume_processing(resume_id: str):
    """
    Dispatches task to Celery queue if available, or falls back to
    asynchronous ThreadPoolExecutor seamlessly.
    """
    dispatched = False
    if celery_app is not None and not settings.CELERY_BROKER_URL.startswith("sqlite"):
        try:
            # Check redis connection / ping briefly
            celery_process_resume.delay(resume_id)
            dispatched = True
            logger.info(f"Dispatched resume {resume_id} to Celery queue.")
        except Exception as e:
            logger.warning(f"Could not queue to Celery broker ({e}), falling back to asynchronous worker thread.")
            dispatched = False
            
    if not dispatched:
        _executor.submit(process_single_resume_pipeline, resume_id)
        logger.info(f"Dispatched resume {resume_id} to async ThreadPool worker.")
