import re
from typing import Dict, Any, Tuple, Optional

# Degree hierarchy and aliases
DEGREE_LEVELS = {
    "phd": {
        "level": 4,
        "patterns": [r'\bph\.?d\b', r'\bdoctor\s+of\s+philosophy\b', r'\bdoctorate\b']
    },
    "masters": {
        "level": 3,
        "patterns": [
            r'\bm\.?s\.?\b', r'\bm\.?tech\b', r'\bmaster(?:[\'’]s)?(?:\s+degree|\s+of\s+science|\s+of\s+engineering|\s+in)?\b',
            r'\bmsc\b', r'\bmca\b', r'\bmba\b'
        ]
    },
    "bachelors": {
        "level": 2,
        "patterns": [
            r'\bb\.?s\.?\b', r'\bb\.?tech\b', r'\bbachelor(?:[\'’]s)?(?:\s+degree|\s+of\s+science|\s+of\s+engineering|\s+in)?\b',
            r'\bbsc\b', r'\bbca\b', r'\bb\.?e\.?\b'
        ]
    },
    "associate": {
        "level": 1,
        "patterns": [r'\bassociate(?:\s+degree)?\b', r'\ba\.?s\.?\b']
    }
}

FIELDS_OF_STUDY = [
    r'computer\s+science', r'information\s+technology', r'software\s+engineering',
    r'data\s+science', r'artificial\s+intelligence', r'electrical\s+engineering',
    r'mathematics', r'statistics', r'physics', r'engineering'
]

def extract_education(text: str) -> Dict[str, Any]:
    """
    Identifies degree level, field of study, and supporting quote from candidate text.
    """
    highest_level = 0
    highest_degree_name = "None detected"
    found_field = None
    evidence_quote = None
    
    text_lower = text.lower()
    
    for degree_name, data in DEGREE_LEVELS.items():
        for pat in data["patterns"]:
            match = re.search(pat, text_lower)
            if match:
                if data["level"] > highest_level:
                    highest_level = data["level"]
                    highest_degree_name = degree_name
                    
                    # Find sentence containing this degree
                    sentences = re.split(r'[\n\.]+', text)
                    for s in sentences:
                        if re.search(pat, s, re.IGNORECASE):
                            evidence_quote = s.strip()[:150]
                            break
                break
                
    for field_pat in FIELDS_OF_STUDY:
        if re.search(field_pat, text_lower):
            found_field = field_pat.replace('\\s+', ' ')
            break
            
    return {
        "degree_level": highest_level,
        "degree_name": highest_degree_name,
        "field_of_study": found_field,
        "evidence": evidence_quote
    }

def evaluate_education_match(required_degree_str: Optional[str], candidate_text: str) -> Tuple[float, str, Optional[str]]:
    """
    Evaluates education match score [0 - 100].
    If role has no specified education requirement, returns 100.0 without penalty.
    """
    if not required_degree_str or not required_degree_str.strip():
        return 100.0, "No formal degree requirement specified for this position.", None
        
    cand_edu = extract_education(candidate_text)
    req_edu = extract_education(required_degree_str)
    
    req_level = req_edu["degree_level"] or 2 # default to bachelors if mentioned
    cand_level = cand_edu["degree_level"]
    
    if cand_level == 0:
        return 30.0, "No formal degree explicitly identified in candidate resume.", cand_edu["evidence"]
        
    if cand_level >= req_level:
        return 100.0, f"Candidate holds {cand_edu['degree_name'].capitalize()} ({cand_edu['field_of_study'] or 'Technical field'}), satisfying the requirement.", cand_edu["evidence"]
    else:
        # Lower degree e.g. Associate when Bachelor required
        return 60.0, f"Candidate holds {cand_edu['degree_name'].capitalize()}, below the required {req_edu['degree_name'].capitalize()}.", cand_edu["evidence"]
