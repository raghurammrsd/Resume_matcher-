from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class MatchEvidenceResponse(BaseModel):
    id: str
    dimension: str
    requirement_text: str
    resume_excerpt: Optional[str] = None
    similarity_score: float
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class MatchResultResponse(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    resume_id: str
    candidate_name: str
    overall_score: float
    skill_score: float
    semantic_score: float
    experience_score: float
    education_score: float
    responsibility_score: float
    status_label: str # Strong, Moderate, Low
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    related_skills: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateDetailAnalysis(BaseModel):
    candidate_id: str
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    resume_id: str
    resume_filename: str
    overall_score: float
    status_label: str
    component_scores: Dict[str, float]
    weights_used: Dict[str, float]
    matched_skills: List[Dict[str, Any]]
    missing_skills: List[str]
    related_skills: List[Dict[str, Any]]
    experience_analysis: Dict[str, Any]
    education_analysis: Dict[str, Any]
    evidence_items: List[MatchEvidenceResponse]
    why_matched: List[str]
    areas_of_concern: List[str]
    fairness_statement: str

class ProcessingStatusResponse(BaseModel):
    job_id: str
    total_resumes: int
    processed_resumes: int
    completed_resumes: int
    failed_resumes: int
    pending_resumes: int
    is_complete: bool
    resumes: List[Dict[str, Any]]
