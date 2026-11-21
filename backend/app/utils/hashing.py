import hashlib
import os

def calculate_file_hash(file_bytes: bytes) -> str:
    """Calculates SHA-256 hash of file content for duplicate detection."""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()

def calculate_file_hash_from_path(file_path: str) -> str:
    """Calculates SHA-256 hash from file path."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()
