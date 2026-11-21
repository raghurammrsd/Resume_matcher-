from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.job import Job, JobRequirement
from backend.app.schemas.job import JobCreate, JobResponse, JobUpdate, RequirementCreate
from backend.app.services.job_extractor import extract_job_requirements

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Creates a new job position."""
    job = Job(
        title=job_in.title,
        description=job_in.description,
        department=job_in.department or "Engineering",
        location=job_in.location or "Remote",
        scoring_weights=job_in.scoring_weights.dict() if job_in.scoring_weights else None
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Automatically extract initial requirements from JD description
    extracted = extract_job_requirements(job_in.description)
    job.required_experience_years = extracted["required_experience_years"]
    
    for skill in extracted["technical_skills"]:
        req = JobRequirement(
            job_id=job.id,
            category="technical_skill",
            requirement_text=skill,
            weight=1.0,
            is_mandatory=False
        )
        db.add(req)
        
    for resp in extracted["responsibilities"]:
        req = JobRequirement(
            job_id=job.id,
            category="responsibility",
            requirement_text=resp,
            weight=1.0,
            is_mandatory=False
        )
        db.add(req)
        
    if extracted["education_qualification"]:
        req = JobRequirement(
            job_id=job.id,
            category="education",
            requirement_text=extracted["education_qualification"],
            weight=1.0,
            is_mandatory=False
        )
        db.add(req)
        
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """Lists all available jobs."""
    return db.query(Job).order_by(Job.created_at.desc()).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Retrieves specific job with requirements."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/analyze", response_model=JobResponse)
def analyze_job_description(job_id: str, db: Session = Depends(get_db)):
    """
    Re-analyzes and extracts structured requirements from the job description text.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    extracted = extract_job_requirements(job.description)
    job.required_experience_years = extracted["required_experience_years"]
    
    # Clear existing requirements to replace with fresh extraction
    db.query(JobRequirement).filter(JobRequirement.job_id == job.id).delete()
    
    for skill in extracted["technical_skills"]:
        db.add(JobRequirement(
            job_id=job.id,
            category="technical_skill",
            requirement_text=skill,
            weight=1.0
        ))
    for resp in extracted["responsibilities"]:
        db.add(JobRequirement(
            job_id=job.id,
            category="responsibility",
            requirement_text=resp,
            weight=1.0
        ))
    if extracted["education_qualification"]:
        db.add(JobRequirement(
            job_id=job.id,
            category="education",
            requirement_text=extracted["education_qualification"],
            weight=1.0
        ))
        
    db.commit()
    db.refresh(job)
    return job

@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_update: JobUpdate, db: Session = Depends(get_db)):
    """Updates job details, requirements, and custom scoring weights."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job_update.title: job.title = job_update.title
    if job_update.description: job.description = job_update.description
    if job_update.department: job.department = job_update.department
    if job_update.location: job.location = job_update.location
    if job_update.required_experience_years is not None:
        job.required_experience_years = job_update.required_experience_years
    if job_update.scoring_weights is not None:
        job.scoring_weights = job_update.scoring_weights.dict()
        
    if job_update.requirements is not None:
        db.query(JobRequirement).filter(JobRequirement.job_id == job.id).delete()
        for req_in in job_update.requirements:
            db.add(JobRequirement(
                job_id=job.id,
                category=req_in.category,
                requirement_text=req_in.requirement_text,
                weight=req_in.weight,
                is_mandatory=req_in.is_mandatory
            ))
            
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Deletes a job position."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return None
