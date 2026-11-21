import pytest
from backend.app.services.experience_extractor import merge_date_intervals, extract_experience, calculate_experience_score

def test_overlapping_date_merging():
    # Job 1: 2020.0 to 2022.0 (2 years)
    # Job 2: 2021.0 to 2023.0 (2 years, overlapping with Job 1 by 1 year)
    # Total merged period should be 2020.0 to 2023.0 = 3.0 years, NOT 4.0 years!
    intervals = [(2020.0, 2022.0), (2021.0, 2023.0)]
    merged_years = merge_date_intervals(intervals)
    assert merged_years == 3.0

def test_extract_experience_from_text():
    text = """
    Software Engineer at TechCorp
    Jan 2020 - Jan 2023
    
    Backend Developer at StartupX
    Jan 2023 - Present
    """
    exp = extract_experience(text)
    assert exp["calculated_years"] >= 6.0

def test_experience_ratio_score():
    # Required: 4 years, Candidate has 3 years -> (3/4)*100 = 75.0
    score, msg = calculate_experience_score(candidate_years=3.0, required_years=4.0)
    assert score == 75.0
    
    # Required: 4 years, Candidate has 5 years -> capped at 100.0
    score_cap, _ = calculate_experience_score(candidate_years=5.0, required_years=4.0)
    assert score_cap == 100.0
