import os
import pytest
from backend.app.services.resume_parser import parse_resume_file
from backend.data.generate_synthetic_resumes import DATA_DIR

def test_parse_valid_pdf():
    pdf_path = os.path.join(DATA_DIR, "Candidate_A_Alex_Rivera.pdf")
    res = parse_resume_file(pdf_path, "Candidate_A_Alex_Rivera.pdf")
    assert res["success"] is True
    assert "Alex Rivera" in res["candidate_name"]
    assert "FastAPI" in res["text"]
    assert "PostgreSQL" in res["text"]

def test_parse_valid_docx():
    docx_path = os.path.join(DATA_DIR, "Candidate_B_Brenda_Vance.docx")
    res = parse_resume_file(docx_path, "Candidate_B_Brenda_Vance.docx")
    assert res["success"] is True
    assert "Brenda" in res["candidate_name"]
    assert "FastAPI" in res["text"]

def test_parse_empty_file():
    empty_path = os.path.join(DATA_DIR, "Invalid_Empty_File.pdf")
    res = parse_resume_file(empty_path, "Invalid_Empty_File.pdf")
    assert res["success"] is False
    assert "empty" in res["error_message"].lower() or "0 pages" in res["error_message"].lower()

def test_parse_corrupt_file():
    corrupt_path = os.path.join(DATA_DIR, "Invalid_Corrupt_File.pdf")
    res = parse_resume_file(corrupt_path, "Invalid_Corrupt_File.pdf")
    assert res["success"] is False
    assert "corrupt" in res["error_message"].lower() or "unreadable" in res["error_message"].lower()

def test_parse_scanned_no_text_file():
    scanned_path = os.path.join(DATA_DIR, "Invalid_Scanned_NoText.pdf")
    res = parse_resume_file(scanned_path, "Invalid_Scanned_NoText.pdf")
    assert res["success"] is False
    assert "ocr required" in res["error_message"].lower()

def test_parse_password_protected_file():
    locked_path = os.path.join(DATA_DIR, "Invalid_Password_Protected.pdf")
    res = parse_resume_file(locked_path, "Invalid_Password_Protected.pdf")
    assert res["success"] is False
    assert "password-protected" in res["error_message"].lower()

def test_unsupported_extension():
    exe_path = os.path.join(DATA_DIR, "Invalid_Unsupported_Executable.exe")
    res = parse_resume_file(exe_path, "Invalid_Unsupported_Executable.exe")
    assert res["success"] is False
    assert "unsupported" in res["error_message"].lower()
