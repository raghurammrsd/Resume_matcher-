import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    match_type = Column(String(50), nullable=False) # explicit, synonym, related
    confidence = Column(Float, default=1.0)
    evidence_text = Column(Text, nullable=True)
    
    candidate = relationship("Candidate", back_populates="skills")
    resume = relationship("Resume", back_populates="skills")

class MatchResult(Base):
    __tablename__ = "match_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Float, nullable=False) # 0 to 100
    skill_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    responsibility_score = Column(Float, default=0.0)
    status_label = Column(String(50), default="Moderate") # Strong, Moderate, Low
    
    model_identifier = Column(String(100), nullable=False)
    weights_used = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="match_results")
    candidate = relationship("Candidate", back_populates="match_results")
    resume = relationship("Resume", back_populates="match_result")
    evidence_items = relationship("MatchEvidence", back_populates="match_result", cascade="all, delete-orphan")

class MatchEvidence(Base):
    __tablename__ = "match_evidence"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    match_result_id = Column(String(36), ForeignKey("match_results.id", ondelete="CASCADE"), nullable=False)
    dimension = Column(String(50), nullable=False) # technical_skill, semantic, experience, education, responsibility
    requirement_text = Column(String(500), nullable=False)
    resume_excerpt = Column(Text, nullable=True)
    similarity_score = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)
    
    match_result = relationship("MatchResult", back_populates="evidence_items")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    model_version = Column(String(100), nullable=False)
    scoring_config = Column(JSON, nullable=False)
    status = Column(String(50), default="processing") # processing, completed, failed
    total_resumes = Column(Integer, default=0)
    processed_resumes = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
