import re
from typing import Dict, List, Tuple, Optional, Any

# Canonical Skill Taxonomy with verified synonyms and related skills
SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "python": {
        "synonyms": ["python", "python3", "py3"],
        "related": ["django", "fastapi", "flask", "numpy", "pandas", "scipy"]
    },
    "fastapi": {
        "synonyms": ["fastapi", "fast-api"],
        "related": ["pydantic", "starlette", "uvicorn", "flask", "django"]
    },
    "postgresql": {
        "synonyms": ["postgresql", "postgres", "psql", "pg"],
        "related": ["sql", "mysql", "sqlite", "relational database", "rdbms"]
    },
    "docker": {
        "synonyms": ["docker", "docker compose", "docker-compose", "containerization"],
        "related": ["kubernetes", "k8s", "podman", "containered"]
    },
    "machine_learning": {
        "synonyms": ["machine learning", "ml", "predictive modeling", "statistical modeling"],
        "related": ["deep learning", "neural networks", "scikit-learn", "tensorflow", "pytorch", "nlp", "computer vision"]
    },
    "kubernetes": {
        "synonyms": ["kubernetes", "k8s"],
        "related": ["docker", "helm", "container orchestration", "openshift"]
    },
    "react": {
        "synonyms": ["react", "react.js", "reactjs"],
        "related": ["next.js", "javascript", "typescript", "redux", "frontend"]
    },
    "typescript": {
        "synonyms": ["typescript", "ts"],
        "related": ["javascript", "js", "node.js"]
    },
    "javascript": {
        "synonyms": ["javascript", "js", "es6", "ecmascript"],
        "related": ["typescript", "node.js", "react", "vue"]
    },
    "redis": {
        "synonyms": ["redis", "in-memory cache", "redis-server"],
        "related": ["memcached", "caching", "celery", "message queue"]
    },
    "celery": {
        "synonyms": ["celery", "distributed task queue"],
        "related": ["redis", "rabbitmq", "background worker", "asynchronous tasks"]
    },
    "git": {
        "synonyms": ["git", "github", "gitlab", "version control"],
        "related": ["ci/cd", "bitbucket", "devops"]
    },
    "aws": {
        "synonyms": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "related": ["cloud computing", "azure", "gcp", "cloud"]
    },
    "pytorch": {
        "synonyms": ["pytorch", "torch"],
        "related": ["deep learning", "tensorflow", "machine learning", "neural networks"]
    },
    "scikit-learn": {
        "synonyms": ["scikit-learn", "sklearn"],
        "related": ["machine learning", "pandas", "numpy", "python"]
    },
    "sql": {
        "synonyms": ["sql", "structured query language", "relational queries"],
        "related": ["postgresql", "mysql", "database", "sqlite"]
    },
    "rest_api": {
        "synonyms": ["rest api", "restful api", "restful", "rest apis", "rest endpoints"],
        "related": ["fastapi", "flask", "api design", "graphql", "microservices"]
    },
    "nlp": {
        "synonyms": ["nlp", "natural language processing", "text processing"],
        "related": ["spacy", "huggingface", "transformers", "bert", "embeddings"]
    },
    "ci_cd": {
        "synonyms": ["ci/cd", "continuous integration", "github actions", "gitlab ci", "jenkins"],
        "related": ["devops", "docker", "automation"]
    },
    "mongodb": {
        "synonyms": ["mongodb", "mongo", "nosql"],
        "related": ["document store", "database", "redis"]
    },
    "java": {
        "synonyms": ["java", "core java", "j2ee"],
        "related": ["spring", "spring boot", "hibernate", "jvm"]
    },
    "golang": {
        "synonyms": ["golang", "go programming", "go lang"],
        "related": ["microservices", "concurrency", "backend"]
    }
}

def canonicalize_skill(skill_query: str) -> Optional[str]:
    """Finds canonical skill key from any alias or synonym."""
    normalized = skill_query.lower().strip()
    # Normalize punctuation e.g. "scikit-learn" / "scikit learn"
    normalized_clean = re.sub(r'[\-_.]', ' ', normalized)
    
    for canonical_name, data in SKILL_TAXONOMY.items():
        if normalized == canonical_name or normalized_clean == canonical_name.replace('_', ' '):
            return canonical_name
        for syn in data["synonyms"]:
            syn_clean = re.sub(r'[\-_.]', ' ', syn)
            if normalized == syn or normalized_clean == syn_clean:
                return canonical_name
    return None

def find_evidence_sentence(text: str, match_term: str) -> Optional[str]:
    """Extracts the specific sentence where the skill was found for recruiter evidence."""
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    term_pattern = re.compile(rf'\b{re.escape(match_term)}\b', re.IGNORECASE)
    
    for s in sentences:
        s_clean = s.strip()
        if term_pattern.search(s_clean):
            # Limit length to 200 chars for clean display
            return s_clean[:220]
    return None

def extract_skills_from_text(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Scans text for all taxonomy skills and records match type and evidence sentence.
    """
    found_skills: Dict[str, Dict[str, Any]] = {}
    text_lower = text.lower()
    
    for canonical, info in SKILL_TAXONOMY.items():
        # Check synonyms / exact terms
        for syn in info["synonyms"]:
            pattern = re.compile(rf'\b{re.escape(syn)}\b', re.IGNORECASE)
            match = pattern.search(text_lower)
            if match:
                evidence = find_evidence_sentence(text, syn)
                match_type = "explicit" if syn == canonical.replace('_', ' ') else "synonym"
                found_skills[canonical] = {
                    "skill_name": canonical,
                    "matched_term": syn,
                    "match_type": match_type,
                    "weight_multiplier": 1.0,
                    "evidence": evidence or f"Mentioned in resume: '{syn}'"
                }
                break
                
    return found_skills

def match_jd_skills(jd_required_skills: List[str], candidate_text: str) -> Dict[str, Any]:
    """
    Matches candidate's resume against JD skills using the 4-tier system:
    - Explicit match: 1.0
    - Verified synonym match: 1.0
    - Explicitly mapped related skill: 0.7
    - No evidence found: 0.0
    """
    candidate_skills = extract_skills_from_text(candidate_text)
    
    matched_explicit = []
    matched_related = []
    missing_skills = []
    total_score = 0.0
    max_possible = len(jd_required_skills) if jd_required_skills else 1.0
    
    for req in jd_required_skills:
        req_clean = req.lower().strip()
        canonical_req = canonicalize_skill(req_clean)
        
        # Check if directly present in candidate skills
        if canonical_req and canonical_req in candidate_skills:
            info = candidate_skills[canonical_req]
            matched_explicit.append({
                "skill": req,
                "canonical": canonical_req,
                "type": info["match_type"],
                "value": 1.0,
                "evidence": info["evidence"]
            })
            total_score += 1.0
        else:
            # Check for explicitly mapped related skill directly in candidate text
            found_related = False
            if canonical_req and canonical_req in SKILL_TAXONOMY:
                related_list = SKILL_TAXONOMY[canonical_req]["related"]
                for rel in related_list:
                    rel_pattern = re.compile(r'\b' + re.escape(rel) + r'\b', re.IGNORECASE)
                    if rel_pattern.search(candidate_text.lower()):
                        evidence = find_evidence_sentence(candidate_text, rel)
                        matched_related.append({
                            "required_skill": req,
                            "related_skill_found": rel,
                            "type": "related",
                            "value": 0.7,
                            "evidence": evidence or f"Demonstrated related proficiency in '{rel}'"
                        })
                        total_score += 0.7
                        found_related = True
                        break
                        
            if not found_related:
                # Direct regex search for exact term as fallback if not in taxonomy
                pattern = re.compile(rf'\b{re.escape(req_clean)}\b', re.IGNORECASE)
                if pattern.search(candidate_text.lower()):
                    evidence = find_evidence_sentence(candidate_text, req_clean)
                    matched_explicit.append({
                        "skill": req,
                        "canonical": req_clean,
                        "type": "explicit",
                        "value": 1.0,
                        "evidence": evidence or f"Found in resume text: '{req}'"
                    })
                    total_score += 1.0
                else:
                    missing_skills.append(req)
                    
    skill_score_100 = round((total_score / max_possible) * 100, 1) if max_possible > 0 else 100.0
    skill_score_100 = min(100.0, max(0.0, skill_score_100))
    
    return {
        "score": skill_score_100,
        "matched_explicit": matched_explicit,
        "matched_related": matched_related,
        "missing_skills": missing_skills,
        "all_candidate_skills": list(candidate_skills.keys())
    }
