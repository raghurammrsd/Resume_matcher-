from typing import List, Dict, Any, Tuple
import numpy as np
from backend.app.ml.embedding_service import encode_texts, compute_cosine_similarity
from backend.app.services.text_cleaner import split_into_chunks

# Calibrated cosine thresholds for all-MiniLM-L6-v2 sentence embeddings
COSINE_MIN_THRESHOLD = 0.18
COSINE_MAX_THRESHOLD = 0.58

def calibrate_similarity_score(raw_cosine: float) -> float:
    """
    Transforms raw vector cosine similarity into a defensible 0-100 score:
    - Below 0.18: completely unrelated (score: 0)
    - Above 0.58: strong semantic alignment (score: 100)
    - Linearly scaled in between
    """
    if raw_cosine <= COSINE_MIN_THRESHOLD:
        return 0.0
    if raw_cosine >= COSINE_MAX_THRESHOLD:
        return 100.0
    scaled = (raw_cosine - COSINE_MIN_THRESHOLD) / (COSINE_MAX_THRESHOLD - COSINE_MIN_THRESHOLD)
    return round(float(scaled * 100.0), 1)

def match_semantic_requirements(
    requirements: List[str], 
    resume_text: str,
    dimension_label: str = "semantic"
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Compares JD requirements against chunked resume text:
    1. Splits resume into semantically rich chunks.
    2. Encodes requirements and resume chunks.
    3. Finds best supporting resume chunk for each requirement.
    4. Computes calibrated similarity and attaches actual supporting text.
    """
    if not requirements or not resume_text.strip():
        return 0.0, []
        
    resume_chunks = split_into_chunks(resume_text, max_chunk_size=120)
    if not resume_chunks:
        return 0.0, []
        
    req_vectors = encode_texts(requirements)
    chunk_vectors = encode_texts(resume_chunks)
    
    evidence_items = []
    total_calibrated_score = 0.0
    
    # Calculate similarity matrix: shape (num_reqs, num_chunks)
    # req_vectors: (N, D), chunk_vectors.T: (D, M) -> sim_matrix: (N, M)
    sim_matrix = np.dot(req_vectors, chunk_vectors.T)
    
    for i, req in enumerate(requirements):
        chunk_sims = sim_matrix[i]
        best_chunk_idx = int(np.argmax(chunk_sims))
        best_cosine = float(chunk_sims[best_chunk_idx])
        best_chunk_text = resume_chunks[best_chunk_idx]
        
        calibrated_score = calibrate_similarity_score(best_cosine)
        total_calibrated_score += calibrated_score
        
        explanation = (
            f"Strong semantic match (Cosine: {best_cosine:.2f})" if calibrated_score >= 80 else
            f"Moderate relevance (Cosine: {best_cosine:.2f})" if calibrated_score >= 50 else
            f"Weak or no direct evidence found (Cosine: {best_cosine:.2f})"
        )
        
        evidence_items.append({
            "dimension": dimension_label,
            "requirement_text": req,
            "resume_excerpt": best_chunk_text[:250],
            "raw_cosine": round(best_cosine, 3),
            "similarity_score": calibrated_score,
            "explanation": explanation
        })
        
    overall_dimension_score = round(total_calibrated_score / len(requirements), 1)
    return overall_dimension_score, evidence_items
