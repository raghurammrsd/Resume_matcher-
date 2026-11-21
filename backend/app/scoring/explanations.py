from typing import Dict, Any, List

FAIRNESS_STATEMENT = (
    "Fairness & Non-Discrimination Notice: TalentMatch AI operates strictly as an objective decision-support "
    "tool. Ranking is based solely on verified technical skills, semantic requirement alignment, verifiable "
    "employment durations, and educational qualifications. Protected personal characteristics (including age, "
    "gender, caste, religion, marital status, nationality, and photographs) are neither extracted nor factored "
    "into scoring calculations."
)

def generate_recruiter_explanations(
    candidate_name: str,
    overall_score: float,
    status_label: str,
    component_scores: Dict[str, float],
    skill_match_data: Dict[str, Any],
    experience_data: Dict[str, Any],
    education_data: Dict[str, Any],
    evidence_items: List[Dict[str, Any]],
    required_years: float
) -> Dict[str, Any]:
    """
    Generates human-readable recruiter explanations highlighting strengths,
    skill coverage, experience relevance, and potential qualification gaps.
    """
    why_matched = []
    areas_of_concern = []
    
    # 1. Technical Skills Explanation
    explicit_matches = skill_match_data.get("matched_explicit", [])
    related_matches = skill_match_data.get("matched_related", [])
    missing_skills = skill_match_data.get("missing_skills", [])
    
    if len(explicit_matches) >= 3:
        skills_str = ", ".join([m["skill"] for m in explicit_matches[:4]])
        why_matched.append(f"Strong verified technical skill coverage ({skills_str}) with explicit supporting evidence in resume.")
    elif len(explicit_matches) > 0:
        skills_str = ", ".join([m["skill"] for m in explicit_matches])
        why_matched.append(f"Demonstrated proficiency in key required skills: {skills_str}.")
        
    for rel in related_matches:
        why_matched.append(
            f"Transferable expertise identified: Found '{rel['related_skill_found']}' related to required '{rel['required_skill']}'."
        )
        
    if missing_skills:
        missing_str = ", ".join(missing_skills)
        areas_of_concern.append(f"No direct evidence found for required skill(s): {missing_str}.")
        
    # 2. Experience Explanation
    cand_years = experience_data.get("final_years", 0.0)
    if required_years > 0:
        if cand_years >= required_years:
            why_matched.append(f"Relevant experience ({cand_years:.1f} years) meets or exceeds the role requirement ({required_years:.1f} years).")
        else:
            areas_of_concern.append(f"Experience duration ({cand_years:.1f} years) is below the preferred minimum of {required_years:.1f} years.")
    else:
        if cand_years > 0:
            why_matched.append(f"Candidate brings {cand_years:.1f} years of practical industry experience.")
            
    if experience_data.get("has_overlapping_intervals"):
        why_matched.append("Employment timeline analysis safely resolved overlapping dates to prevent duplicate experience counting.")
        
    # 3. Education Explanation
    if component_scores.get("education", 100.0) >= 80.0:
        if education_data.get("evidence"):
            why_matched.append(f"Educational qualification aligned: {education_data['evidence']}.")
    else:
        areas_of_concern.append("Academic degree level is below the preferred qualification specified in the job description.")
        
    # 4. Responsibilities / Semantic Alignment
    resp_score = component_scores.get("responsibility", 0.0)
    sem_score = component_scores.get("semantic", 0.0)
    
    if resp_score >= 75.0 or sem_score >= 75.0:
        why_matched.append("Strong semantic alignment between candidate's past work achievements and target role responsibilities.")
    elif resp_score < 50.0:
        areas_of_concern.append("Limited semantic overlap between candidate's documented project accomplishments and core day-to-day responsibilities.")
        
    if not why_matched:
        why_matched.append("Candidate demonstrates baseline foundational qualifications.")
        
    return {
        "why_matched": why_matched,
        "areas_of_concern": areas_of_concern,
        "fairness_statement": FAIRNESS_STATEMENT
    }
