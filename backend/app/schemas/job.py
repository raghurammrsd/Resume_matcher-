from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class RequirementBase(BaseModel):
    category: str # technical_skill, experience, education, responsibility
    requirement_text: str
    weight: float = 1.0
    is_mandatory: bool = False

class RequirementCreate(RequirementBase):
    pass

class RequirementResponse(RequirementBase):
    id: str
    job_id: str

    class Config:
        from_attributes = True

class ScoringWeightsSchema(BaseModel):
    weight_skills: float = 0.35
    weight_semantic: float = 0.25
    weight_experience: float = 0.20
    weight_education: float = 0.10
    weight_responsibility: float = 0.10

class JobCreate(BaseModel):
    title: str = Field(..., example="Senior AI Engineer")
    description: str = Field(..., example="We are looking for an AI Engineer with Python, FastAPI, Docker, and PostgreSQL.")
    department: Optional[str] = "Engineering"
    location: Optional[str] = "Remote"
    scoring_weights: Optional[ScoringWeightsSchema] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    required_experience_years: Optional[float] = None
    scoring_weights: Optional[ScoringWeightsSchema] = None
    requirements: Optional[List[RequirementCreate]] = None

class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    department: str
    location: str
    required_experience_years: float
    scoring_weights: Optional[Dict[str, float]] = None
    created_at: datetime
    updated_at: datetime
    requirements: List[RequirementResponse] = []

    class Config:
        from_attributes = True
