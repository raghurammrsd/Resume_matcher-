from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class CandidateSkillResponse(BaseModel):
    id: str
    skill_name: str
    match_type: str
    confidence: float
    evidence_text: Optional[str] = None

    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: str
    created_at: datetime
    skills: List[CandidateSkillResponse] = []

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    file_size: int
    error_message: Optional[str] = None
    file_hash: str
    created_at: datetime

    class Config:
        from_attributes = True
