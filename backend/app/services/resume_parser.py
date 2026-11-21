import os
import re
from typing import Dict, Any, Tuple
import pymupdf # PyMuPDF
import docx
from backend.app.core.logging import logger
from backend.app.services.text_cleaner import clean_text
from backend.app.core.security import sanitize_extracted_text

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?')

def extract_contact_info(text: str, filename: str) -> Tuple[str, str, str]:
    """
    Extracts Candidate Name, Email, and Phone number.
    Uses filename as sensible fallback if name is not distinctly formatted on line 1.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Candidate name is typically on first or second non-empty line
    name = "Candidate"
    if lines:
        first_line = lines[0]
        # Ignore lines with email, phone, or links
        if len(first_line) < 40 and not '@' in first_line and not any(c.isdigit() for c in first_line):
            name = first_line
        elif len(lines) > 1 and len(lines[1]) < 40 and not '@' in lines[1]:
            name = lines[1]
            
    # If name still fallback, derive from filename (e.g. "Candidate_A_Resume.pdf" -> "Candidate A")
    if name == "Candidate":
        base = os.path.splitext(filename)[0]
        cleaned_base = re.sub(r'[-_]?(?:resume|cv|profile)[-_]?', '', base, flags=re.IGNORECASE)
        cleaned_base = cleaned_base.replace('_', ' ').replace('-', ' ').strip()
        if cleaned_base:
            name = cleaned_base.title()
            
    # Extract Email
    emails = EMAIL_REGEX.findall(text)
    email = emails[0] if emails else "not_provided@example.com"
    
    # Extract Phone
    phone_match = PHONE_REGEX.search(text)
    phone = phone_match.group(0).strip() if phone_match else None
    
    return name, email, phone

def parse_pdf(file_path: str) -> Tuple[bool, str, str]:
    """
    Parses PDF using PyMuPDF (fitz).
    Handles password protection, corruption, empty files, and scanned non-text PDFs.
    """
    try:
        doc = pymupdf.open(file_path)
        
        # Check password protection
        if doc.is_encrypted:
            doc.close()
            return False, "", "File is password-protected and cannot be parsed."
            
        if doc.page_count == 0:
            doc.close()
            return False, "", "PDF contains 0 pages."
            
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        
        full_text = "\n".join(text_parts).strip()
        
        # Check for scanned PDF / image-only PDF with negligible text
        if len(full_text) < 40:
            return False, "", "Scanned PDF: Document contains no selectable text (OCR required)."
            
        return True, full_text, "Success"
        
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return False, "", f"Corrupt or unreadable PDF: {str(e)}"

def parse_docx(file_path: str) -> Tuple[bool, str, str]:
    """
    Parses DOCX documents including standard paragraphs and table contents.
    """
    try:
        doc = docx.Document(file_path)
        text_parts = []
        
        # 1. Paragraphs & Bullet Points
        for p in doc.paragraphs:
            if p.text.strip():
                text_parts.append(p.text)
                
        # 2. Table Cells (resumes often layout education / skills in tables)
        for table in doc.tables:
            for row in table.rows:
                row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_texts:
                    text_parts.append(" | ".join(row_texts))
                    
        full_text = "\n".join(text_parts).strip()
        
        if len(full_text) < 30:
            return False, "", "Empty or nearly empty DOCX file."
            
        return True, full_text, "Success"
        
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        return False, "", f"Corrupt or unreadable DOCX: {str(e)}"

def parse_resume_file(file_path: str, original_filename: str) -> Dict[str, Any]:
    """
    High-level parser entrypoint:
    Validates, extracts text, cleans text, and sanitizes against prompt injection.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        success, raw_text, message = parse_pdf(file_path)
    elif ext == ".docx":
        success, raw_text, message = parse_docx(file_path)
    else:
        return {
            "success": False,
            "error_message": f"Unsupported format '{ext}'. Only .pdf and .docx are supported.",
            "text": "",
            "candidate_name": "",
            "email": "",
            "phone": ""
        }
        
    if not success:
        return {
            "success": False,
            "error_message": message,
            "text": "",
            "candidate_name": "",
            "email": "",
            "phone": ""
        }
        
    cleaned = clean_text(raw_text)
    sanitized = sanitize_extracted_text(cleaned)
    name, email, phone = extract_contact_info(sanitized, original_filename)
    
    return {
        "success": True,
        "error_message": None,
        "text": sanitized,
        "candidate_name": name,
        "email": email,
        "phone": phone
    }
