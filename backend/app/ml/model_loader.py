import threading
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

_model_instance = None
_lock = threading.Lock()

def get_sentence_transformer():
    """
    Thread-safe Singleton loader for SentenceTransformer.
    Ensures the embedding model is loaded strictly once per worker/process.
    """
    global _model_instance
    if _model_instance is None:
        with _lock:
            if _model_instance is None:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME} on {settings.DEVICE}...")
                try:
                    from sentence_transformers import SentenceTransformer
                    _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device=settings.DEVICE)
                    logger.info("SentenceTransformer model successfully loaded into memory.")
                except Exception as e:
                    logger.error(f"Failed to load SentenceTransformer: {e}")
                    raise e
    return _model_instance
