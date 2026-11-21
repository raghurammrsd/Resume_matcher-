import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), index=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(50), default="pending") # pending, parsing, matching, completed, failed
    error_message = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    parsed_metadata = Column(JSON, nullable=True) # experience_years, education, detected_sections, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="resumes")
    candidate = relationship("Candidate", back_populates="resumes")
    match_result = relationship("MatchResult", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="resume", cascade="all, delete-orphan")
