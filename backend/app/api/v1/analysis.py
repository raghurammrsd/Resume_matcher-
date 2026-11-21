from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.db.session import get_db
from backend.app.models.job import Job
from backend.app.models.resume import Resume
from backend.app.models.match import MatchResult
from backend.app.tasks.processing_tasks import dispatch_resume_processing

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/jobs/{job_id}/summary")
def get_job_analysis_summary(job_id: str, db: Session = Depends(get_db)):
    """
    Returns high-level statistics for the recruiter dashboard:
    - total candidates processed
    - average match score
    - count of strong matches (score >= 80)
    - count of moderate matches (60-79)
    - count of low matches (< 60)
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job position not found")
        
    results = db.query(MatchResult).filter(MatchResult.job_id == job_id).all()
    resumes = db.query(Resume).filter(Resume.job_id == job_id).all()
    
    total_processed = len(results)
    avg_score = round(sum(r.overall_score for r in results) / total_processed, 1) if total_processed > 0 else 0.0
    strong_count = sum(1 for r in results if r.overall_score >= 80.0)
    moderate_count = sum(1 for r in results if 60.0 <= r.overall_score < 80.0)
    low_count = sum(1 for r in results if r.overall_score < 60.0)
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "total_resumes_uploaded": len(resumes),
        "total_candidates_processed": total_processed,
        "average_match_score": avg_score,
        "strong_matches_count": strong_count,
        "moderate_matches_count": moderate_count,
        "low_matches_count": low_count,
        "scoring_weights": job.scoring_weights
    }

@router.post("/jobs/{job_id}/reprocess")
def reprocess_all_resumes(job_id: str, db: Session = Depends(get_db)):
    """
    Triggers re-matching for all completed/failed resumes in a job
    (e.g., after modifying requirements or weights).
    """
    resumes = db.query(Resume).filter(Resume.job_id == job_id).all()
    requeued_count = 0
    for r in resumes:
        if r.status != "pending":
            r.status = "pending"
            r.error_message = None
            db.commit()
            dispatch_resume_processing(r.id)
            requeued_count += 1
            
    return {"message": f"Successfully queued {requeued_count} resumes for reprocessing."}
