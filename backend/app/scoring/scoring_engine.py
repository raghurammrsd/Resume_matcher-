from typing import Dict, Any, List
from backend.app.scoring.weights import get_normalized_weights

def compute_overall_match(
    component_scores: Dict[str, float],
    active_dimensions: Dict[str, bool],
    custom_weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Computes final match score:
    FinalScore = w_S * S + w_M * M + w_E * E + w_Q * Q + w_R * R
    Each dimension is bounded [0, 100].
    """
    weights = get_normalized_weights(custom_weights, active_dimensions)
    
    final_score = 0.0
    for dim, weight in weights.items():
        score = component_scores.get(dim, 0.0)
        bounded_score = min(100.0, max(0.0, score))
        final_score += weight * bounded_score
        
    final_score = round(min(100.0, max(0.0, final_score)), 1)
    
    # Assign status tier
    if final_score >= 80.0:
        status_label = "Strong"
    elif final_score >= 60.0:
        status_label = "Moderate"
    else:
        status_label = "Low"
        
    return {
        "overall_score": final_score,
        "status_label": status_label,
        "component_scores": {k: round(v, 1) for k, v in component_scores.items()},
        "weights_used": weights
    }
