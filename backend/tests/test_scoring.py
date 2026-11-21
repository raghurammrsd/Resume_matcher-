import pytest
from backend.app.scoring.weights import get_normalized_weights
from backend.app.scoring.scoring_engine import compute_overall_match

def test_weight_normalization_and_redistribution():
    # If education is not required, active_dimensions["education"] = False
    active = {
        "skills": True,
        "semantic": True,
        "experience": True,
        "education": False, # Inactive
        "responsibility": True
    }
    weights = get_normalized_weights(custom_weights=None, active_dimensions=active)
    
    assert "education" not in weights
    assert round(sum(weights.values()), 2) == 1.00
    # Original sum was 0.90, so weights should scale up proportionally
    assert weights["skills"] > 0.35

def test_scoring_bounds():
    scores = {
        "skills": 95.0,
        "semantic": 90.0,
        "experience": 85.0,
        "education": 100.0,
        "responsibility": 92.0
    }
    active = {k: True for k in scores}
    result = compute_overall_match(scores, active)
    
    assert 90.0 <= result["overall_score"] <= 95.0
    assert result["status_label"] == "Strong"
