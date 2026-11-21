import os
import time
import queue
import threading
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import SessionLocal
from backend.app.models.job import Job
from backend.app.models.resume import Resume
from backend.app.services.resume_parser import parse_resume_file
from backend.app.services.matching_service import match_resume_to_job

# Robust in-memory background queue to eliminate database lock contention
_task_queue = queue.Queue()

def _worker_loop():
    """Single consumer daemon thread processing resumes sequentially to ensure 0 database lock errors."""
    while True:
        resume_id = _task_queue.get()
        try:
            process_single_resume_pipeline(resume_id)
        except Exception as e:
            logger.error(f"Queue worker exception for resume {resume_id}: {e}", exc_info=True)
        finally:
            _task_queue.task_done()

# Start background queue consumer thread
_worker_thread = threading.Thread(target=_worker_loop, daemon=True, name="ResumeQueueWorker")
_worker_thread.start()

def process_single_resume_pipeline(resume_id: str, max_retries: int = 3):
    """
    Core pipeline to parse an uploaded resume, extract metadata, and run AI matching.
    Includes automatic retries for temporary locks and handles malformed files cleanly.
    """
    for attempt in range(max_retries):
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
            return # Succeeded
            
        except OperationalError as oe:
            db.rollback()
            if "locked" in str(oe).lower() and attempt < max_retries - 1:
                logger.warning(f"Database busy for {resume_id}, retrying ({attempt + 1}/{max_retries})...")
                time.sleep(0.5 * (attempt + 1))
                continue
            else:
                logger.error(f"Database operational error processing resume {resume_id}: {oe}")
                _record_failure(resume_id, f"Database error: {str(oe)}")
                return
        except Exception as e:
            logger.error(f"Unexpected error processing resume {resume_id}: {str(e)}", exc_info=True)
            _record_failure(resume_id, f"Processing error: {str(e)}")
            return
        finally:
            db.close()

def _record_failure(resume_id: str, error_msg: str):
    db: Session = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.status = "failed"
            resume.error_message = error_msg
            db.commit()
    except Exception as e:
        logger.error(f"Failed to record failure state for {resume_id}: {e}")
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
    Dispatches task to Celery queue if available, or enqueues into
    the serialized background worker thread.
    """
    dispatched = False
    if celery_app is not None and not settings.CELERY_BROKER_URL.startswith("sqlite"):
        try:
            celery_process_resume.delay(resume_id)
            dispatched = True
            logger.info(f"Dispatched resume {resume_id} to Celery queue.")
        except Exception as e:
            logger.warning(f"Could not queue to Celery broker ({e}), falling back to in-memory queue.")
            dispatched = False
            
    if not dispatched:
        _task_queue.put(resume_id)
        logger.info(f"Enqueued resume {resume_id} into in-memory queue (Queue depth: {_task_queue.qsize()}).")
