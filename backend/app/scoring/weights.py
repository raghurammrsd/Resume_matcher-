from typing import Dict, Optional
from backend.app.core.config import settings

def get_normalized_weights(custom_weights: Optional[Dict[str, float]], active_dimensions: Dict[str, bool]) -> Dict[str, float]:
    """
    Normalizes weights and proportionally redistributes weights
    if an entire dimension is not applicable or not required by the JD.
    """
    base_weights = {
        "skills": settings.DEFAULT_WEIGHT_SKILLS,
        "semantic": settings.DEFAULT_WEIGHT_SEMANTIC,
        "experience": settings.DEFAULT_WEIGHT_EXPERIENCE,
        "education": settings.DEFAULT_WEIGHT_EDUCATION,
        "responsibility": settings.DEFAULT_WEIGHT_RESPONSIBILITY,
    }
    
    if custom_weights:
        for k in base_weights.keys():
            if k in custom_weights and custom_weights[k] is not None:
                base_weights[k] = float(custom_weights[k])
                
    # Filter only active dimensions
    filtered_weights = {}
    total_active_weight = 0.0
    for dim, is_active in active_dimensions.items():
        if is_active and dim in base_weights:
            filtered_weights[dim] = base_weights[dim]
            total_active_weight += base_weights[dim]
            
    if total_active_weight <= 0:
        # Uniform fallback
        num_active = len(filtered_weights) or 1
        return {k: 1.0 / num_active for k in filtered_weights}
        
    # Proportionally redistribute so sum equals 1.0
    normalized = {k: round(v / total_active_weight, 4) for k, v in filtered_weights.items()}
    return normalized
