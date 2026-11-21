import hashlib
from typing import List, Union
import numpy as np
from backend.app.ml.model_loader import get_sentence_transformer

# Memory cache for computed embeddings
_embedding_cache = {}

def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def encode_texts(texts: List[str]) -> np.ndarray:
    """
    Encodes a list of texts into L2-normalized numpy vectors.
    Uses in-memory cache to skip redundant calculations.
    """
    if not texts:
        return np.empty((0, 384))
        
    model = get_sentence_transformer()
    uncached_indices = []
    uncached_texts = []
    vectors = [None] * len(texts)
    
    for i, t in enumerate(texts):
        h = get_text_hash(t.strip())
        if h in _embedding_cache:
            vectors[i] = _embedding_cache[h]
        else:
            uncached_indices.append(i)
            uncached_texts.append(t.strip())
            
    if uncached_texts:
        new_embeddings = model.encode(uncached_texts, normalize_embeddings=True, show_progress_bar=False)
        for idx, orig_pos in enumerate(uncached_indices):
            vec = new_embeddings[idx]
            h = get_text_hash(uncached_texts[idx])
            _embedding_cache[h] = vec
            vectors[orig_pos] = vec
            
    return np.array(vectors)

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Computes cosine similarity between two 1D or 2D normalized vectors."""
    # Since vectors are L2 normalized, dot product is identical to cosine similarity
    dot = np.dot(vec1, vec2)
    return float(np.clip(dot, -1.0, 1.0))
