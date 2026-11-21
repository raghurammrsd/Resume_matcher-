from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.job import Job
from backend.app.models.candidate import Candidate
from backend.app.models.resume import Resume
from backend.app.models.match import MatchResult, MatchEvidence, CandidateSkill
from backend.app.schemas.candidate import CandidateResponse
from backend.app.schemas.analysis import MatchResultResponse, CandidateDetailAnalysis, MatchEvidenceResponse
from backend.app.services.skill_extractor import match_jd_skills
from backend.app.services.experience_extractor import extract_experience
from backend.app.services.education_extractor import extract_education
from backend.app.scoring.explanations import generate_recruiter_explanations

router = APIRouter(tags=["Candidates & Ranking"])

@router.get("/jobs/{job_id}/candidates", response_model=List[MatchResultResponse])
def get_ranked_candidates(
    job_id: str,
    status_filter: Optional[str] = Query(None, description="Filter by status: Strong, Moderate, Low"),
    min_score: Optional[float] = Query(None, description="Minimum overall score"),
    db: Session = Depends(get_db)
):
    """
    Returns ranked candidates for a specific job, ordered by overall match score descending.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job position not found")
        
    query = db.query(MatchResult).filter(MatchResult.job_id == job_id)
    
    if status_filter:
        query = query.filter(MatchResult.status_label.ilike(status_filter))
    if min_score is not None:
        query = query.filter(MatchResult.overall_score >= min_score)
        
    results = query.order_by(MatchResult.overall_score.desc()).all()
    
    # Required skills from JD
    jd_skills = [r.requirement_text for r in job.requirements if r.category == "technical_skill"]
    
    response_items = []
    for mr in results:
        candidate = db.query(Candidate).filter(Candidate.id == mr.candidate_id).first()
        resume = db.query(Resume).filter(Resume.id == mr.resume_id).first()
        
        cand_name = candidate.name if candidate else (resume.filename if resume else "Candidate")
        
        # Determine matched and missing skills
        skills_matched = db.query(CandidateSkill).filter(
            CandidateSkill.candidate_id == mr.candidate_id,
            CandidateSkill.resume_id == mr.resume_id
        ).all()
        
        matched_names = [s.skill_name for s in skills_matched if s.match_type in ["explicit", "synonym"]]
        related_items = [{"skill": s.skill_name, "confidence": s.confidence} for s in skills_matched if s.match_type == "related"]
        
        # Calculate missing skills against JD
        cand_text = resume.raw_text or "" if resume else ""
        skill_analysis = match_jd_skills(jd_skills, cand_text)
        missing_skills = skill_analysis["missing_skills"]
        
        response_items.append({
            "id": mr.id,
            "job_id": mr.job_id,
            "candidate_id": mr.candidate_id,
            "resume_id": mr.resume_id,
            "candidate_name": cand_name,
            "overall_score": mr.overall_score,
            "skill_score": mr.skill_score,
            "semantic_score": mr.semantic_score,
            "experience_score": mr.experience_score,
            "education_score": mr.education_score,
            "responsibility_score": mr.responsibility_score,
            "status_label": mr.status_label,
            "matched_skills": matched_names,
            "missing_skills": missing_skills,
            "related_skills": related_items,
            "created_at": mr.created_at
        })
        
    return response_items

@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Retrieves candidate profile details."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.get("/candidates/{candidate_id}/explanation", response_model=CandidateDetailAnalysis)
def get_candidate_explanation(
    candidate_id: str,
    job_id: Optional[str] = Query(None, description="Target Job ID"),
    db: Session = Depends(get_db)
):
    """
    Returns complete explainability report with supporting evidence excerpts,
    component breakdown, experience analysis, strengths, and areas of concern.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    query = db.query(MatchResult).filter(MatchResult.candidate_id == candidate_id)
    if job_id:
        query = query.filter(MatchResult.job_id == job_id)
    match_result = query.order_by(MatchResult.created_at.desc()).first()
    
    if not match_result:
        raise HTTPException(status_code=404, detail="No match analysis found for this candidate")
        
    job = db.query(Job).filter(Job.id == match_result.job_id).first()
    resume = db.query(Resume).filter(Resume.id == match_result.resume_id).first()
    
    # Collect evidence items
    evidence_models = db.query(MatchEvidence).filter(MatchEvidence.match_result_id == match_result.id).all()
    evidence_list = [
        MatchEvidenceResponse(
            id=ev.id,
            dimension=ev.dimension,
            requirement_text=ev.requirement_text,
            resume_excerpt=ev.resume_excerpt,
            similarity_score=ev.similarity_score,
            explanation=ev.explanation
        ) for ev in evidence_models
    ]
    
    # Skills analysis
    jd_skills = [r.requirement_text for r in job.requirements if r.category == "technical_skill"] if job else []
    resume_text = resume.raw_text or "" if resume else ""
    skill_match_data = match_jd_skills(jd_skills, resume_text)
    
    # Experience analysis
    exp_data = extract_experience(resume_text)
    
    # Education analysis
    edu_data = extract_education(resume_text)
    
    component_scores = {
        "technical_skills": match_result.skill_score,
        "semantic_similarity": match_result.semantic_score,
        "relevant_experience": match_result.experience_score,
        "education": match_result.education_score,
        "responsibilities": match_result.responsibility_score
    }
    
    explanations = generate_recruiter_explanations(
        candidate_name=candidate.name,
        overall_score=match_result.overall_score,
        status_label=match_result.status_label,
        component_scores={
            "skills": match_result.skill_score,
            "semantic": match_result.semantic_score,
            "experience": match_result.experience_score,
            "education": match_result.education_score,
            "responsibility": match_result.responsibility_score
        },
        skill_match_data=skill_match_data,
        experience_data=exp_data,
        education_data=edu_data,
        evidence_items=[ev.dict() for ev in evidence_list],
        required_years=job.required_experience_years if job else 0.0
    )
    
    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "resume_id": resume.id if resume else "",
        "resume_filename": resume.filename if resume else "",
        "overall_score": match_result.overall_score,
        "status_label": match_result.status_label,
        "component_scores": component_scores,
        "weights_used": match_result.weights_used,
        "matched_skills": skill_match_data["matched_explicit"],
        "missing_skills": skill_match_data["missing_skills"],
        "related_skills": skill_match_data["matched_related"],
        "experience_analysis": exp_data,
        "education_analysis": edu_data,
        "evidence_items": evidence_list,
        "why_matched": explanations["why_matched"],
        "areas_of_concern": explanations["areas_of_concern"],
        "fairness_statement": explanations["fairness_statement"]
    }
