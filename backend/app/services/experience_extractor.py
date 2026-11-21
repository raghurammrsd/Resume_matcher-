import re
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

MONTHS = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'september': 9, 'sept': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12
}

CURRENT_YEAR = 2026 # Context reference date

# Date range pattern: e.g. "Jan 2020 - Mar 2023", "05/2019 - Present", "2018 - 2021"
DATE_RANGE_PATTERN = re.compile(
    r'(?P<start_month>[a-zA-Z]{3,9}|[0-1]?\d)?\s*[\/\-\.,]?\s*(?P<start_year>(?:19|20)\d{2})'
    r'\s*(?:-|–|—|to|until)\s*'
    r'(?:(?P<end_month>[a-zA-Z]{3,9}|[0-1]?\d)?\s*[\/\-\.,]?\s*(?P<end_year>(?:19|20)\d{2})|(?P<present>present|current|now|ongoing))',
    re.IGNORECASE
)

EXPLICIT_EXP_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+relevant)?\s+experience',
    re.IGNORECASE
)

def parse_month(month_str: Optional[str]) -> int:
    if not month_str:
        return 1
    m_clean = month_str.lower().strip()
    if m_clean.isdigit():
        val = int(m_clean)
        return val if 1 <= val <= 12 else 1
    return MONTHS.get(m_clean, 1)

def merge_date_intervals(intervals: List[Tuple[float, float]]) -> float:
    """
    Merges overlapping date intervals to avoid double-counting simultaneous employments.
    Intervals are represented as decimal years (e.g., 2020.0 to 2022.5).
    """
    if not intervals:
        return 0.0
        
    # Sort intervals by start time
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    
    current_start, current_end = sorted_intervals[0]
    for start, end in sorted_intervals[1:]:
        if start <= current_end:
            # Overlapping interval - extend end if necessary
            current_end = max(current_end, end)
        else:
            # Non-overlapping interval
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    
    # Calculate total duration in years
    total_years = sum(end - start for start, end in merged)
    return round(total_years, 1)

def extract_experience(text: str) -> Dict[str, Any]:
    """
    Extracts employment periods, calculates non-overlapping experience,
    and identifies explicitly stated experience.
    """
    intervals: List[Tuple[float, float]] = []
    detected_ranges = []
    
    for match in DATE_RANGE_PATTERN.finditer(text):
        m_dict = match.groupdict()
        start_year = int(m_dict['start_year'])
        start_month = parse_month(m_dict['start_month'])
        start_val = start_year + (start_month - 1) / 12.0
        
        if m_dict['present']:
            end_val = CURRENT_YEAR + (11 / 12.0) # Nov 2026
            end_str = "Present"
        else:
            end_year = int(m_dict['end_year'])
            end_month = parse_month(m_dict['end_month'])
            end_val = end_year + (end_month - 1) / 12.0
            end_str = f"{end_year}"
            
        if end_val >= start_val and (end_val - start_val) <= 40:
            intervals.append((start_val, end_val))
            detected_ranges.append(f"{start_year} - {end_str}")
            
    calculated_years = merge_date_intervals(intervals)
    
    # Check for explicitly stated experience in text (e.g., "5+ years of experience")
    explicit_matches = EXPLICIT_EXP_PATTERN.findall(text)
    explicit_years = float(explicit_matches[0]) if explicit_matches else None
    
    # Final verified years: if calculated is reasonable, prefer calculated non-overlapping,
    # or fall back to explicit statement if dates were not cleanly parsed
    final_years = calculated_years if calculated_years > 0 else (explicit_years or 0.0)
    
    return {
        "calculated_years": calculated_years,
        "explicit_stated_years": explicit_years,
        "final_years": final_years,
        "detected_date_ranges": detected_ranges,
        "has_overlapping_intervals": len(intervals) > 1 and calculated_years < sum(e - s for s, e in intervals)
    }

def calculate_experience_score(candidate_years: float, required_years: float) -> Tuple[float, str]:
    """
    Calculates experience score:
    ExperienceScore = min(CandidateYears / RequiredYears, 1.0) * 100
    """
    if required_years <= 0:
        return 100.0, "No minimum experience required for this role."
        
    ratio = min(candidate_years / required_years, 1.0)
    score = round(ratio * 100.0, 1)
    
    if candidate_years >= required_years:
        explanation = f"Candidate possesses {candidate_years:.1f} years of relevant experience, meeting or exceeding the required {required_years:.1f} years (100% score)."
    else:
        explanation = f"Candidate has {candidate_years:.1f} years out of {required_years:.1f} required years ({score:.1f}% proportional score)."
        
    return score, explanation
