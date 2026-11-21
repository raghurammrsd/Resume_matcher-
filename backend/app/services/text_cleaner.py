import re
import unicodedata
from typing import Dict, List

SECTION_HEADERS = {
    "experience": re.compile(r'^(?:work\s+)?experience|employment|work\s+history|professional\s+experience', re.IGNORECASE),
    "education": re.compile(r'^education|academic\s+background|qualifications|degrees?', re.IGNORECASE),
    "skills": re.compile(r'^(?:technical\s+)?skills|technologies|core\s+competencies|tooling', re.IGNORECASE),
    "projects": re.compile(r'^projects|key\s+projects|personal\s+projects', re.IGNORECASE),
    "summary": re.compile(r'^summary|professional\s+summary|objective|profile|about\s+me', re.IGNORECASE),
}

def clean_text(text: str) -> str:
    """
    Normalizes unicode, standardizes whitespace, repairs split hyphenated words.
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Standardize quotation marks and dashes
    text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('–', '-').replace('—', '-')
    
    # Replace non-breaking spaces and form feeds
    text = text.replace('\xa0', ' ').replace('\x0c', '\n')
    
    # Fix hyphenated words broken across line wraps (e.g., "devel-\noper" -> "developer")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    # Replace multiple spaces with a single space while keeping line breaks
    lines = [re.sub(r'[ \t]+', ' ', line.strip()) for line in text.splitlines()]
    
    # Remove consecutive empty lines
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned_lines.append("")
            prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
            
    return "\n".join(cleaned_lines).strip()

def split_into_chunks(text: str, max_chunk_size: int = 300) -> List[str]:
    """
    Splits text into meaningful semantic chunks (paragraphs or bullet points).
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_len = 0
    
    for p in paragraphs:
        words = p.split()
        if current_len + len(words) > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
        current_chunk.append(p)
        current_len += len(words)
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks if chunks else [text]

def extract_sections(text: str) -> Dict[str, str]:
    """
    Segments resume text into distinct sections (skills, experience, education, projects, etc.).
    """
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {
        "summary": [],
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "other": []
    }
    
    current_section = "summary"
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Check if line matches a section header (usually short, <= 40 chars)
        if len(line_stripped) <= 40:
            header_found = False
            for sec, pattern in SECTION_HEADERS.items():
                if pattern.match(line_stripped):
                    current_section = sec
                    header_found = True
                    break
            if header_found:
                continue
                
        sections[current_section].append(line_stripped)
        
    return {k: "\n".join(v).strip() for k, v in sections.items()}
