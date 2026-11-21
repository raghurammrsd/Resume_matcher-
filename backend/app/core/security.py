import os
import uuid
import re

# Disallowed prompt injection patterns that malicious candidates might insert
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+must", re.IGNORECASE),
    re.compile(r"output\s+a\s+score\s+of\s+100", re.IGNORECASE),
    re.compile(r"override\s+score", re.IGNORECASE)
]

def sanitize_extracted_text(text: str) -> str:
    """
    Sanitizes extracted resume text to neutralize adversarial prompt injection attempts.
    """
    cleaned = text
    for pattern in INJECTION_PATTERNS:
        cleaned = pattern.sub("[SUSPICIOUS_PROMPT_DIRECTIVE_REMOVED]", cleaned)
    return cleaned

def generate_safe_filename(original_filename: str) -> str:
    """
    Generates a secure server-side UUID filename preserving valid extension.
    Never trusts client-supplied filenames for disk operations.
    """
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        ext = ".bin"
    return f"{uuid.uuid4().hex}{ext}"
