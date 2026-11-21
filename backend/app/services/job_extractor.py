import re
from typing import Dict, List, Any
from backend.app.services.skill_extractor import SKILL_TAXONOMY, canonicalize_skill
from backend.app.services.text_cleaner import clean_text

EXPERIENCE_REQ_PATTERN = re.compile(
    r'(?:at\s+least|minimum|min|requires?)\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
    re.IGNORECASE
)
EXP_RANGE_PATTERN = re.compile(
    r'(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years?|yrs?)',
    re.IGNORECASE
)
EDUCATION_PATTERNS = [
    re.compile(r'(?:bachelor(?:[\'’]s)?|b\.?s\.?|b\.?tech|master(?:[\'’]s)?|m\.?s\.?|m\.?tech|ph\.?d)[^.\n]*', re.IGNORECASE)
]

def extract_job_requirements(jd_text: str) -> Dict[str, Any]:
    """
    Parses Job Description text and categorizes requirements into:
    - Technical skills
    - Minimum experience years
    - Education qualification
    - Core job responsibilities
    """
    cleaned_jd = clean_text(jd_text)
    jd_lower = cleaned_jd.lower()
    
    # 1. Extract Skills
    detected_skills = []
    for canonical, info in SKILL_TAXONOMY.items():
        for syn in info["synonyms"]:
            pattern = re.compile(rf'\b{re.escape(syn)}\b', re.IGNORECASE)
            if pattern.search(jd_lower):
                detected_skills.append(canonical.replace('_', ' ').title())
                break
                
    # Fallback to default core tech skills if none detected
    if not detected_skills:
        detected_skills = ["Python", "PostgreSQL", "Docker", "REST API"]
        
    # Deduplicate while preserving order
    unique_skills = list(dict.fromkeys(detected_skills))
    
    # 2. Extract Minimum Experience Years
    req_years = 0.0
    exp_matches = EXPERIENCE_REQ_PATTERN.findall(cleaned_jd)
    if exp_matches:
        req_years = float(exp_matches[0])
    else:
        range_matches = EXP_RANGE_PATTERN.findall(cleaned_jd)
        if range_matches:
            req_years = float(range_matches[0][0])
            
    # 3. Extract Education
    education_req = None
    for pat in EDUCATION_PATTERNS:
        match = pat.search(cleaned_jd)
        if match:
            education_req = match.group(0).strip()
            break
            
    # 4. Extract Responsibilities
    # Look for bullet points or lines following "responsibilities", "what you will do", etc.
    lines = cleaned_jd.splitlines()
    responsibilities = []
    in_resp_section = False
    
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
            
        lower_line = line_s.lower()
        if any(h in lower_line for h in ["responsibilities", "what you'll do", "duties", "you will"]):
            in_resp_section = True
            continue
        elif any(h in lower_line for h in ["requirements", "qualifications", "skills", "benefits", "what we offer"]):
            if in_resp_section and responsibilities:
                in_resp_section = False
                
        if in_resp_section:
            # Bullet point or action line
            if line_s.startswith(('-', '*', '•', '–')) or (len(line_s) > 20 and line_s[0].isupper()):
                clean_bullet = re.sub(r'^[-*•–\d\.]+\s*', '', line_s)
                if len(clean_bullet) >= 15:
                    responsibilities.append(clean_bullet)
                    
    # If no explicitly separated responsibilities found, extract action-oriented sentences
    if not responsibilities:
        sentences = re.split(r'[.\n]+', cleaned_jd)
        for s in sentences:
            s_s = s.strip()
            if any(s_s.lower().startswith(w) for w in ["build", "design", "develop", "maintain", "deploy", "collaborate", "architect", "lead"]):
                if len(s_s) >= 20:
                    responsibilities.append(s_s)
                    
    return {
        "technical_skills": unique_skills,
        "required_experience_years": req_years,
        "education_qualification": education_req or "Bachelor's degree in Computer Science or equivalent field",
        "responsibilities": responsibilities[:6] if responsibilities else [
            "Develop scalable backend services and APIs",
            "Build and maintain data and machine learning pipelines",
            "Deploy and containerize microservices in cloud environments"
        ]
    }
