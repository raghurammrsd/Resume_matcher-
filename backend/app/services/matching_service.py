from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.job import Job
from backend.app.models.candidate import Candidate
from backend.app.models.resume import Resume
from backend.app.models.match import CandidateSkill, MatchResult, MatchEvidence
from backend.app.services.skill_extractor import match_jd_skills
from backend.app.services.experience_extractor import extract_experience, calculate_experience_score
from backend.app.services.education_extractor import evaluate_education_match
from backend.app.ml.semantic_matcher import match_semantic_requirements
from backend.app.scoring.scoring_engine import compute_overall_match
from backend.app.scoring.explanations import generate_recruiter_explanations

def match_resume_to_job(db: Session, job: Job, resume: Resume) -> MatchResult:
    """
    Executes the complete 5-dimension AI matching pipeline for a single resume against a job.
    Saves candidate details, extracted skills, scores, and supporting evidence to the database.
    """
    resume_text = resume.raw_text or ""
    
    # 1. Categorize Job Requirements
    skill_reqs = [r.requirement_text for r in job.requirements if r.category == "technical_skill"]
    resp_reqs = [r.requirement_text for r in job.requirements if r.category == "responsibility"]
    edu_reqs = [r.requirement_text for r in job.requirements if r.category == "education"]
    edu_target = edu_reqs[0] if edu_reqs else "Bachelor's degree in Computer Science or related"
    
    # 2. Dimension A: Technical Skills Matching (35%)
    skill_match_data = match_jd_skills(skill_reqs, resume_text)
    skill_score = skill_match_data["score"]
    
    # Precompute resume chunks and vectors ONCE to maximize performance
    from backend.app.services.text_cleaner import split_into_chunks
    from backend.app.ml.embedding_service import encode_texts
    resume_chunks = split_into_chunks(resume_text, max_chunk_size=120)
    chunk_vectors = encode_texts(resume_chunks) if resume_chunks else None
    
    # 3. Dimension B: Semantic Similarity on Role Scope & Core Requirements (25%)
    sem_context_reqs = [f"Role: {job.title}. {job.description[:220]}"]
    for r in job.requirements:
        if r.category in ["responsibility", "education"]:
            sem_context_reqs.append(r.requirement_text)
    sem_score, sem_evidence = match_semantic_requirements(
        sem_context_reqs, 
        resume_text, 
        dimension_label="semantic",
        precomputed_chunks=resume_chunks,
        precomputed_chunk_vectors=chunk_vectors
    )
    
    # 4. Dimension C: Relevant Experience (20%)
    experience_data = extract_experience(resume_text)
    exp_score, exp_explanation = calculate_experience_score(
        experience_data["final_years"], 
        job.required_experience_years
    )
    
    # 5. Dimension D: Education and Qualifications (10%)
    edu_score, edu_explanation, edu_quote = evaluate_education_match(edu_target, resume_text)
    education_data = {
        "score": edu_score,
        "explanation": edu_explanation,
        "evidence": edu_quote
    }
    
    # 6. Dimension E: Job Responsibility Alignment (10%)
    if resp_reqs:
        resp_score, resp_evidence = match_semantic_requirements(
            resp_reqs, 
            resume_text, 
            dimension_label="responsibility",
            precomputed_chunks=resume_chunks,
            precomputed_chunk_vectors=chunk_vectors
        )
    else:
        resp_score, resp_evidence = sem_score, []
        
    # Active dimensions check for proportional weight redistribution
    active_dimensions = {
        "skills": len(skill_reqs) > 0,
        "semantic": True,
        "experience": job.required_experience_years > 0,
        "education": len(edu_reqs) > 0,
        "responsibility": len(resp_reqs) > 0
    }
    
    component_scores = {
        "skills": skill_score,
        "semantic": sem_score,
        "experience": exp_score,
        "education": edu_score,
        "responsibility": resp_score
    }
    
    # Compute Final Weighted Match Score
    overall_data = compute_overall_match(
        component_scores=component_scores,
        active_dimensions=active_dimensions,
        custom_weights=job.scoring_weights
    )
    
    # Combine All Evidence Items
    all_evidence = []
    
    # Technical skills evidence
    for m in skill_match_data["matched_explicit"]:
        all_evidence.append({
            "dimension": "technical_skill",
            "requirement_text": f"Required Skill: {m['skill']}",
            "resume_excerpt": m["evidence"],
            "similarity_score": 100.0,
            "explanation": f"Explicit match for '{m['skill']}'"
        })
    for m in skill_match_data["matched_related"]:
        all_evidence.append({
            "dimension": "technical_skill",
            "requirement_text": f"Required Skill: {m['required_skill']}",
            "resume_excerpt": m["evidence"],
            "similarity_score": 70.0,
            "explanation": f"Related skill match: found '{m['related_skill_found']}'"
        })
        
    # Experience evidence
    all_evidence.append({
        "dimension": "experience",
        "requirement_text": f"Minimum Experience: {job.required_experience_years:.1f} years",
        "resume_excerpt": f"Calculated: {experience_data['final_years']:.1f} non-overlapping years. Ranges: {', '.join(experience_data['detected_date_ranges'][:3])}",
        "similarity_score": exp_score,
        "explanation": exp_explanation
    })
    
    # Education evidence
    all_evidence.append({
        "dimension": "education",
        "requirement_text": f"Qualification: {edu_target}",
        "resume_excerpt": edu_quote or "Document inspection",
        "similarity_score": edu_score,
        "explanation": edu_explanation
    })
    
    # Semantic & Responsibility evidence
    all_evidence.extend(sem_evidence)
    all_evidence.extend(resp_evidence)
    
    # Create or update candidate record
    candidate_name = resume.parsed_metadata.get("candidate_name", "Candidate") if resume.parsed_metadata else "Candidate"
    email = resume.parsed_metadata.get("email") if resume.parsed_metadata else None
    phone = resume.parsed_metadata.get("phone") if resume.parsed_metadata else None
    
    candidate = resume.candidate
    if not candidate:
        candidate = Candidate(
            name=candidate_name,
            email=email,
            phone=phone
        )
        db.add(candidate)
        db.flush()
        resume.candidate_id = candidate.id
    else:
        candidate.name = candidate_name
        if email: candidate.email = email
        if phone: candidate.phone = phone
        
    # Remove existing candidate skills and match result for idempotency
    db.query(CandidateSkill).filter(CandidateSkill.resume_id == resume.id).delete()
    db.query(MatchResult).filter(MatchResult.resume_id == resume.id).delete()
    db.flush()
    
    # Store Extracted Skills
    for m in skill_match_data["matched_explicit"]:
        skill_rec = CandidateSkill(
            candidate_id=candidate.id,
            resume_id=resume.id,
            skill_name=m["canonical"],
            match_type="explicit",
            confidence=1.0,
            evidence_text=m["evidence"]
        )
        db.add(skill_rec)
        
    for m in skill_match_data["matched_related"]:
        skill_rec = CandidateSkill(
            candidate_id=candidate.id,
            resume_id=resume.id,
            skill_name=m["related_skill_found"],
            match_type="related",
            confidence=0.7,
            evidence_text=m["evidence"]
        )
        db.add(skill_rec)
        
    # Store MatchResult
    match_result = MatchResult(
        job_id=job.id,
        candidate_id=candidate.id,
        resume_id=resume.id,
        overall_score=overall_data["overall_score"],
        skill_score=component_scores["skills"],
        semantic_score=component_scores["semantic"],
        experience_score=component_scores["experience"],
        education_score=component_scores["education"],
        responsibility_score=component_scores["responsibility"],
        status_label=overall_data["status_label"],
        model_identifier=settings.EMBEDDING_MODEL_NAME,
        weights_used=overall_data["weights_used"]
    )
    db.add(match_result)
    db.flush()
    
    # Store Supporting Evidence Excerpts
    for ev in all_evidence:
        ev_rec = MatchEvidence(
            match_result_id=match_result.id,
            dimension=ev["dimension"],
            requirement_text=ev["requirement_text"],
            resume_excerpt=ev["resume_excerpt"],
            similarity_score=ev["similarity_score"],
            explanation=ev["explanation"]
        )
        db.add(ev_rec)
        
    resume.status = "completed"
    db.commit()
    db.refresh(match_result)
    
    logger.info(f"Successfully matched resume '{resume.filename}' for candidate '{candidate.name}': Overall Score = {overall_data['overall_score']}")
    return match_result
