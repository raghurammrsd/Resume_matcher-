import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import engine
from backend.app.db.base import Base
from backend.app.api.v1 import jobs, resumes, candidates, analysis

# Initialize tables on startup
Base.metadata.create_all(bind=engine)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent AI-Powered Resume Matching & Candidate Intelligence Platform"
)

# Configure CORS for Frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(resumes.router, prefix=settings.API_V1_STR)
app.include_router(candidates.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def seed_benchmark_job():
    """Seeds the benchmark AI Engineer position on first startup if database is empty."""
    from backend.app.db.session import SessionLocal
    from backend.app.models.job import Job, JobRequirement
    from backend.app.services.job_extractor import extract_job_requirements
    
    db = SessionLocal()
    try:
        if db.query(Job).count() == 0:
            logger.info("Database empty: Seeding default benchmark Senior AI Engineer position...")
            default_jd = (
                "Role: Senior AI Engineer\n"
                "We are looking for an AI & Backend Engineer with at least 4 years of experience to design, build, "
                "and deploy scalable REST APIs with FastAPI, develop ML pipelines, and deploy Docker microservices backed by PostgreSQL.\n\n"
                "Responsibilities:\n"
                "- Develop scalable REST APIs and high-throughput backend services using FastAPI and Python\n"
                "- Build, evaluate, and maintain scalable machine learning pipelines\n"
                "- Containerize microservices using Docker and deploy to cloud environments\n"
                "- Optimize PostgreSQL database schemas, indexing, and queries\n\n"
                "Required Skills & Qualifications:\n"
                "- Minimum 4+ years of relevant software engineering experience\n"
                "- Expertise in Python, FastAPI, PostgreSQL, Docker, and Machine Learning\n"
                "- Bachelor's degree in Computer Science or equivalent"
            )
            job = Job(
                title="Senior AI Engineer",
                department="Engineering",
                location="Remote / Hybrid",
                description=default_jd,
                required_experience_years=4.0,
                scoring_weights={
                    "weight_skills": 0.35,
                    "weight_semantic": 0.25,
                    "weight_experience": 0.20,
                    "weight_education": 0.10,
                    "weight_responsibility": 0.10
                }
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
            extracted = extract_job_requirements(default_jd)
            for s in extracted["technical_skills"]:
                db.add(JobRequirement(job_id=job.id, category="technical_skill", requirement_text=s))
            for r in extracted["responsibilities"]:
                db.add(JobRequirement(job_id=job.id, category="responsibility", requirement_text=r))
            if extracted["education_qualification"]:
                db.add(JobRequirement(job_id=job.id, category="education", requirement_text=extracted["education_qualification"]))
            db.commit()
            logger.info(f"Successfully seeded benchmark job: {job.title} (ID: {job.id})")
    except Exception as e:
        logger.warning(f"Startup seeding warning: {e}")
    finally:
        db.close()

@app.get("/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "embedding_model": settings.EMBEDDING_MODEL_NAME
    }

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }
