import os
from typing import List, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentMatch AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./talentmatch.db")
    
    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Upload limits
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE_MB: int = 15
    MAX_BATCH_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    
    # ML / Embedding
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DEVICE: str = "cpu"
    
    # Default Scoring Weights
    DEFAULT_WEIGHT_SKILLS: float = 0.35
    DEFAULT_WEIGHT_SEMANTIC: float = 0.25
    DEFAULT_WEIGHT_EXPERIENCE: float = 0.20
    DEFAULT_WEIGHT_EDUCATION: float = 0.10
    DEFAULT_WEIGHT_RESPONSIBILITY: float = 0.10
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
