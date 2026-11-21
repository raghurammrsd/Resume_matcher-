import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.session import Base
from backend.app.models.job import Job, JobRequirement
from backend.app.models.resume import Resume
from backend.app.services.matching_service import match_resume_to_job
from backend.app.services.resume_parser import parse_resume_file
from backend.data.generate_synthetic_resumes import DATA_DIR, CANDIDATES

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_ai_engineer_candidate_ranking(test_db):
    """
    Evaluates Candidate A through J against AI Engineer JD requiring:
    - Technical skills: Python, FastAPI, PostgreSQL, Machine Learning, Docker
    - Experience: 4.0 years
    - Education: Bachelor's in CS
    - Responsibilities: Scalable backend APIs, ML pipelines, Docker containerization
    
    Verifies that the hybrid AI matching engine accurately ranks strong matches
    above weaker candidates without hardcoding any scores!
    """
    job = Job(
        title="AI Engineer",
        description="Senior AI Engineer required to build scalable REST APIs with FastAPI, develop ML pipelines, and deploy Docker microservices backed by PostgreSQL.",
        required_experience_years=4.0
    )
    test_db.add(job)
    test_db.commit()
    
    # Add JD requirements
    skills = ["Python", "FastAPI", "PostgreSQL", "Machine Learning", "Docker"]
    for s in skills:
        test_db.add(JobRequirement(job_id=job.id, category="technical_skill", requirement_text=s))
        
    resps = [
        "Develop high-throughput REST APIs and backend services",
        "Build and maintain scalable machine learning pipelines",
        "Containerize microservices using Docker"
    ]
    for r in resps:
        test_db.add(JobRequirement(job_id=job.id, category="responsibility", requirement_text=r))
        
    test_db.add(JobRequirement(
        job_id=job.id, 
        category="education", 
        requirement_text="Bachelor's degree in Computer Science or equivalent"
    ))
    test_db.commit()
    
    candidate_scores = {}
    
    for cand in CANDIDATES:
        file_path = os.path.join(DATA_DIR, cand["filename"])
        parsed = parse_resume_file(file_path, cand["filename"])
        assert parsed["success"] is True
        
        resume = Resume(
            job_id=job.id,
            filename=cand["filename"],
            file_hash="hash_" + cand["name"],
            file_path=file_path,
            file_size=1024,
            status="pending",
            raw_text=parsed["text"],
            parsed_metadata={
                "candidate_name": parsed["candidate_name"],
                "email": parsed["email"],
                "phone": parsed["phone"]
            }
        )
        test_db.add(resume)
        test_db.commit()
        
        match_result = match_resume_to_job(test_db, job, resume)
        candidate_scores[cand["name"]] = match_result.overall_score
        
    # Verify rankings
    score_A = candidate_scores["Alex Rivera"]
    score_B = candidate_scores["Brenda Vance"]
    score_C = candidate_scores["Carlos Mendez"]
    score_D = candidate_scores["David Kim"]
    score_F = candidate_scores["Frank Miller"]
    score_J = candidate_scores["Jamal Williams"]
    
    print("\n--- Model Evaluation Results ---")
    for name, sc in sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"{name:25s}: {sc:.1f}%")
        
    # Assertions derived from scenario expectations:
    # 1. Candidate A has all skills, experience, and responsibilities -> Top score (>= 88%)
    assert score_A >= 88.0, f"Candidate A should have a high score, got {score_A}"
    
    # 2. Candidate A must beat Candidate B (B is missing ML evidence)
    assert score_A > score_B, f"Candidate A ({score_A}) should rank higher than Candidate B ({score_B})"
    
    # 3. Candidate B (Strong backend) must beat Candidate D (Java developer)
    assert score_B > score_D, f"Candidate B ({score_B}) should beat Java-only Candidate D ({score_D})"
    
    # 4. Java-only (D) and PHP/WordPress (F) developers should rank lower than Python/ML candidates
    assert score_A > score_F, f"Candidate A ({score_A}) should beat Candidate F ({score_F})"
    assert score_D < 60.0 or score_D < score_A
    assert score_F < 50.0, f"Candidate F should be low, got {score_F}"
