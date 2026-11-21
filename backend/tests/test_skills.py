import pytest
from backend.app.services.skill_extractor import match_jd_skills, canonicalize_skill

def test_canonicalize_skill():
    assert canonicalize_skill("python3") == "python"
    assert canonicalize_skill("psql") == "postgresql"
    assert canonicalize_skill("k8s") == "kubernetes"
    assert canonicalize_skill("docker-compose") == "docker"

def test_explicit_skill_match():
    jd_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    candidate_text = "Experienced software engineer with 4 years in Python, FastAPI, and PostgreSQL. Built Docker containers."
    result = match_jd_skills(jd_skills, candidate_text)
    
    assert result["score"] == 100.0
    assert len(result["matched_explicit"]) == 4
    assert len(result["missing_skills"]) == 0

def test_related_skill_match():
    # Candidate knows Django/Flask (related to FastAPI), MySQL (related to PostgreSQL)
    jd_skills = ["FastAPI", "PostgreSQL"]
    candidate_text = "Proficient in Django REST APIs and MySQL relational databases."
    result = match_jd_skills(jd_skills, candidate_text)
    
    # 2 related skills at 0.7 each -> score = (1.4 / 2.0) * 100 = 70.0
    assert result["score"] == 70.0
    assert len(result["matched_related"]) == 2
    assert len(result["missing_skills"]) == 0

def test_missing_skills():
    jd_skills = ["Kubernetes", "Golang", "AWS"]
    candidate_text = "Java developer working with Spring Boot and Oracle database."
    result = match_jd_skills(jd_skills, candidate_text)
    
    assert result["score"] == 0.0
    assert len(result["missing_skills"]) == 3
