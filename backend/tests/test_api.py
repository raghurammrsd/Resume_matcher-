import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.data.generate_synthetic_resumes import DATA_DIR

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_complete_api_workflow():
    # 1. Create a job
    job_payload = {
        "title": "Full Stack AI Developer",
        "description": "Seeking an engineer proficient in Python, FastAPI, Docker, and PostgreSQL. Minimum 3 years experience.",
        "department": "Engineering",
        "location": "Hybrid",
        "scoring_weights": {
            "weight_skills": 0.35,
            "weight_semantic": 0.25,
            "weight_experience": 0.20,
            "weight_education": 0.10,
            "weight_responsibility": 0.10
        }
    }
    create_res = client.post("/api/v1/jobs", json=job_payload)
    assert create_res.status_code == 201
    job_data = create_res.json()
    job_id = job_data["id"]
    assert job_id is not None
    assert len(job_data["requirements"]) > 0
    
    # 2. Upload candidate resumes
    pdf_path_A = os.path.join(DATA_DIR, "Candidate_A_Alex_Rivera.pdf")
    docx_path_B = os.path.join(DATA_DIR, "Candidate_B_Brenda_Vance.docx")
    
    with open(pdf_path_A, "rb") as f1, open(docx_path_B, "rb") as f2:
        files = [
            ("files", ("Candidate_A_Alex_Rivera.pdf", f1, "application/pdf")),
            ("files", ("Candidate_B_Brenda_Vance.docx", f2, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
        ]
        upload_res = client.post(f"/api/v1/jobs/{job_id}/resumes", files=files)
        assert upload_res.status_code == 200
        uploaded_resumes = upload_res.json()
        assert len(uploaded_resumes) == 2
        resume_id_A = uploaded_resumes[0]["id"]
        
    # Wait for background processing (or process directly)
    import time
    for _ in range(20):
        status_res = client.get(f"/api/v1/jobs/{job_id}/status")
        assert status_res.status_code == 200
        st = status_res.json()
        if st["completed_resumes"] >= 2 or st["is_complete"]:
            break
        time.sleep(0.5)
        
    # 3. Check candidates ranking
    candidates_res = client.get(f"/api/v1/jobs/{job_id}/candidates")
    assert candidates_res.status_code == 200
    ranked = candidates_res.json()
    assert len(ranked) >= 2
    top_cand = ranked[0]
    assert top_cand["overall_score"] > 0
    candidate_id = top_cand["candidate_id"]
    
    # 4. Check candidate explanation
    exp_res = client.get(f"/api/v1/candidates/{candidate_id}/explanation?job_id={job_id}")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "why_matched" in exp_data
    assert len(exp_data["why_matched"]) > 0
    assert "fairness_statement" in exp_data
    assert "component_scores" in exp_data
    
    # 5. Delete resume
    del_res = client.delete(f"/api/v1/resumes/{resume_id_A}")
    assert del_res.status_code == 204
