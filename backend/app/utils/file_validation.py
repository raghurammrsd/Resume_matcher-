import os
from typing import Tuple

# Magic byte signatures
PDF_MAGIC = b"%PDF"
DOCX_MAGIC = b"PK\x03\x04"

def validate_file_content(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validates file extension and binary magic signature.
    Prevents executable or disguised files from being processed.
    """
    if not file_bytes:
        return False, "File is completely empty (0 bytes)."
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        return False, f"Unsupported file extension '{ext}'. Only .pdf and .docx are supported."
    
    if ext == ".pdf":
        if not file_bytes.startswith(PDF_MAGIC):
            return False, "File header mismatch: Not a valid PDF file (invalid magic signature)."
    elif ext == ".docx":
        if not file_bytes.startswith(DOCX_MAGIC):
            return False, "File header mismatch: Not a valid DOCX file (invalid zip magic signature)."
            
    return True, "Valid"
