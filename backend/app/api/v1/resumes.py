import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.security import generate_safe_filename
from backend.app.db.session import get_db
from backend.app.models.job import Job
from backend.app.models.resume import Resume
from backend.app.schemas.candidate import ResumeUploadResponse
from backend.app.schemas.analysis import ProcessingStatusResponse
from backend.app.utils.hashing import calculate_file_hash
from backend.app.utils.file_validation import validate_file_content
from backend.app.tasks.processing_tasks import dispatch_resume_processing

router = APIRouter(tags=["Resumes"])

@router.post("/jobs/{job_id}/resumes", response_model=List[ResumeUploadResponse])
async def upload_resumes_bulk(
    job_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Bulk uploads candidate resumes (PDF / DOCX).
    Validates file signatures, prevents duplicate reprocessing via SHA-256,
    and dispatches background extraction and AI matching tasks.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job position not found")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    uploaded_responses = []
    total_batch_size = 0
    
    for file in files:
        contents = await file.read()
        file_size = len(contents)
        total_batch_size += file_size
        
        # Check max individual size
        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
            )
            
        # Check batch limit
        if total_batch_size > settings.MAX_BATCH_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Total upload batch exceeds {settings.MAX_BATCH_SIZE_MB}MB limit."
            )
            
        file_hash = calculate_file_hash(contents)
        
        # Check duplicate upload for this job
        existing_resume = db.query(Resume).filter(
            Resume.job_id == job_id,
            Resume.file_hash == file_hash
        ).first()
        
        if existing_resume:
            logger.info(f"Duplicate resume detected ({file.filename}) with hash {file_hash[:8]}. Returning existing record.")
            uploaded_responses.append(existing_resume)
            continue
            
        # Validate magic binary signature
        is_valid, validation_msg = validate_file_content(contents, file.filename)
        
        # Generate safe server-side storage filename
        stored_filename = generate_safe_filename(file.filename)
        stored_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
        
        with open(stored_path, "wb") as f:
            f.write(contents)
            
        resume = Resume(
            job_id=job_id,
            filename=file.filename,
            file_hash=file_hash,
            file_path=stored_path,
            file_size=file_size,
            status="pending" if is_valid else "failed",
            error_message=None if is_valid else validation_msg
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        if is_valid:
            dispatch_resume_processing(resume.id)
            
        uploaded_responses.append(resume)
        
    return uploaded_responses

@router.get("/jobs/{job_id}/status", response_model=ProcessingStatusResponse)
def get_job_processing_status(job_id: str, db: Session = Depends(get_db)):
    """
    Tracks real-time processing status of all uploaded resumes for a job.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    resumes = db.query(Resume).filter(Resume.job_id == job_id).all()
    total = len(resumes)
    completed = sum(1 for r in resumes if r.status == "completed")
    failed = sum(1 for r in resumes if r.status == "failed")
    pending = sum(1 for r in resumes if r.status in ["pending", "parsing", "matching"])
    
    resume_list = []
    for r in resumes:
        resume_list.append({
            "id": r.id,
            "filename": r.filename,
            "status": r.status,
            "file_size": r.file_size,
            "error_message": r.error_message,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
        
    return {
        "job_id": job_id,
        "total_resumes": total,
        "processed_resumes": completed + failed,
        "completed_resumes": completed,
        "failed_resumes": failed,
        "pending_resumes": pending,
        "is_complete": total > 0 and pending == 0,
        "resumes": resume_list
    }

@router.post("/jobs/{job_id}/load-sample-resumes", response_model=List[ResumeUploadResponse])
def load_sample_resumes(job_id: str, db: Session = Depends(get_db)):
    """
    Convenience endpoint to load all 15 pre-generated synthetic and edge-case resumes
    (10 benchmark candidates + 5 invalid/corrupt files) into the target job for instant evaluation.
    """
    import shutil
    from backend.data.generate_synthetic_resumes import DATA_DIR
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job position not found")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(DATA_DIR):
        raise HTTPException(status_code=500, detail="Sample resumes directory not found")
        
    loaded_resumes = []
    for filename in sorted(os.listdir(DATA_DIR)):
        source_path = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(source_path) or filename.startswith('.'):
            continue
            
        with open(source_path, "rb") as f:
            contents = f.read()
            
        file_hash = calculate_file_hash(contents)
        
        # Check duplicate
        existing = db.query(Resume).filter(
            Resume.job_id == job_id,
            Resume.file_hash == file_hash
        ).first()
        
        if existing:
            loaded_resumes.append(existing)
            continue
            
        stored_filename = generate_safe_filename(filename)
        dest_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
        shutil.copyfile(source_path, dest_path)
        
        is_valid, validation_msg = validate_file_content(contents, filename)
        
        resume = Resume(
            job_id=job_id,
            filename=filename,
            file_hash=file_hash,
            file_path=dest_path,
            file_size=len(contents),
            status="pending" if is_valid else "failed",
            error_message=None if is_valid else validation_msg
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        if is_valid:
            dispatch_resume_processing(resume.id)
            
        loaded_resumes.append(resume)
        
    return loaded_resumes

@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """
    Deletes a resume and cleans up its stored file on disk.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Remove file on disk if exists
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete resume file on disk: {e}")
            
    db.delete(resume)
    db.commit()
    return None
