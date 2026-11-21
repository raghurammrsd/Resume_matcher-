import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String(100), default="Engineering")
    location = Column(String(100), default="Remote / Hybrid")
    required_experience_years = Column(Float, default=0.0)
    scoring_weights = Column(JSON, nullable=True) # Customizable weights
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="job", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")

class JobRequirement(Base):
    __tablename__ = "job_requirements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False) # technical_skill, experience, education, responsibility
    requirement_text = Column(String(500), nullable=False)
    weight = Column(Float, default=1.0)
    is_mandatory = Column(Boolean, default=False)
    
    job = relationship("Job", back_populates="requirements")
