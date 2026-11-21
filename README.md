# TalentMatch AI: Resume Matching and Candidate Intelligence Platform

## Overview

TalentMatch AI is an automated resume screening and candidate intelligence system engineered for recruiters and hiring managers. It evaluates candidate resumes against structured job descriptions using a hybrid matching architecture that combines canonical skill taxonomy verification with dense semantic vector embeddings.

Rather than relying on basic keyword searches, the system assesses candidate suitability across five distinct dimensions: technical skills, semantic requirement alignment, verifiable work experience duration, education and qualifications, and job responsibility match. Every evaluation produces a 0–100 composite score accompanied by human-readable explanations, extracted resume excerpts, and a clear breakdown of matched versus missing competencies.

---

## Architectural Design

The platform is designed as a modular monolith. The system separates user-facing dashboard logic from background file parsing and machine learning inference, ensuring that processing large resume batches does not degrade user interface responsiveness.

### Core Components

1. **Frontend Client (React, TypeScript, Tailwind CSS)**
   - Single-page application built on React 18, Vite, and Tailwind CSS.
   - Provides five primary workflows: live analytics dashboard, job creation with automated requirement extraction, drag-and-drop batch resume upload, sortable candidate ranking tables, and comprehensive candidate profile audit modals.

2. **Backend API (FastAPI, Python 3.11+)**
   - Implements a RESTful interface using FastAPI and Pydantic schemas.
   - Enforces strict input validation, file size limits, MIME type inspection, and binary signature verification.
   - Exposes documented OpenAPI endpoints (`/docs`) for job management, document ingestion, asynchronous status tracking, and candidate explanations.

3. **Document Ingestion and Parsing Engine**
   - PyMuPDF (`pymupdf`) handles PDF text extraction, metadata parsing, and page structure analysis.
   - `python-docx` handles DOCX files, extracting standard text, lists, and structured table cells.
   - Fault-tolerant parser design isolates file-level failures (such as corrupt files, 0-byte uploads, password encryption, or scanned image documents) so that an invalid file never terminates batch processing for other resumes.

4. **Natural Language Processing and Semantic Search**
   - Canonical skill taxonomy maps industry skills, standard aliases, and related technologies.
   - Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`) converts requirement descriptions and resume text chunks into 384-dimensional dense vectors.
   - A thread-safe singleton model loader ensures weights are loaded once in memory per worker process rather than per document.

5. **Data Persistence and Asynchronous Processing**
   - SQLAlchemy 2.0 ORM supports SQLite for local development and PostgreSQL for production environments.
   - Celery and Redis manage background task queues for production worker pools, with an automatic asynchronous ThreadPool fallback for self-contained local developer environments.

---

## The Matching and Scoring Engine

The scoring model assesses candidates across five evaluation dimensions, weighted to reflect standard hiring priorities. The system uses a 100-point composite model:

Final Score = (0.35 * Skills) + (0.25 * Semantic) + (0.20 * Experience) + (0.10 * Education) + (0.10 * Responsibilities)

### 1. Technical Skill Matching (35% Weight)
The system extracts technical proficiencies and matches them against job requirements using a four-tier taxonomy:
- **Explicit Match (1.0)**: The exact skill term appears in the resume text with supporting context.
- **Verified Synonym (1.0)**: A recognized alias appears in the resume (for example, "PostgreSQL", "Postgres", and "psql" map to the same canonical database skill).
- **Explicitly Mapped Related Skill (0.7)**: The candidate lacks the exact tool but demonstrates proficiency in a directly related framework (for example, demonstrating "Django" or "Flask" when "FastAPI" is requested).
- **No Evidence Found (0.0)**: No mention or direct evidence appears in the document.

The engine requires explicit resume evidence and never assumes a candidate possesses a technical skill based purely on semantic similarity.

### 2. Semantic Requirement Similarity (25% Weight)
Using `all-MiniLM-L6-v2`, the engine chunks job requirements and resume bodies, generates L2-normalized embeddings, and calculates cosine similarity.
- Raw cosine similarity values for sentence embeddings typically fall between 0.18 (unrelated) and 0.58+ (strong semantic equivalence).
- The system applies a calibrated mapping function: similarity values below 0.18 receive a score of 0, values at or above 0.58 receive 100, and intermediate values scale linearly.
- For each requirement, the system records the highest-scoring candidate text chunk as verifiable evidence.

### 3. Relevant Work Experience (20% Weight)
The experience module extracts employment dates and calculates total non-overlapping duration:
- **Simultaneous Employment Merging**: If a candidate worked two overlapping roles between 2021 and 2023, the merger calculates the union of the date intervals (2.0 years), preventing double-counting.
- **Ratio Scoring**: Score = min(Candidate Years / Required Years, 1.0) * 100.
- If no minimum experience is required by the role, this dimension awards full marks or redistributes its weight.

### 4. Education and Academic Qualifications (10% Weight)
The engine identifies academic degrees (Ph.D., Master's, Bachelor's/B.Tech, Associate) and relevant technical fields (Computer Science, Software Engineering, Mathematics, Data Science). If a role does not require a formal academic credential, the candidate is not penalized.

### 5. Responsibility Alignment (10% Weight)
Core responsibilities from the job description are compared against candidate project descriptions and day-to-day duties using semantic similarity, ensuring the candidate has performed comparable functional tasks.

### Dynamic Weight Redistribution
If a specific dimension is genuinely not required by a given job description (for instance, an entry-level role with no minimum years or no degree requirement), that dimension is deactivated. Its weight is proportionally redistributed across the remaining active criteria so that candidates are never scored down for unrequested qualifications.

---

## Document Parsing and Error Handling

Real-world resumes vary widely in formatting, structure, and readability. The ingestion pipeline includes specific safeguards:

- **Empty Files**: Detects 0-byte or 0-page uploads and reports a clear validation error.
- **Corrupt Documents**: Handles malformed binary streams gracefully and records an informative error without interrupting the batch.
- **Password-Protected Files**: Detects encrypted PDFs using document permission flags and flags the file for recruiter follow-up.
- **Scanned / Image-Only PDFs**: Checks extracted text density. If a multi-page document yields under 40 characters of selectable text, the system flags the file as requiring OCR rather than assigning an inaccurate 0% score.
- **DOCX Formats**: Parses standard paragraphs, bullet point styles, and multi-cell tables where technical summaries and education are frequently placed.
- **Deduplication**: Calculates SHA-256 hashes on upload. Submitting the identical resume file multiple times returns the existing record rather than creating duplicate processing overhead.
- **Prompt Injection Defense**: Sanitizes extracted text by stripping adversarial directives (such as instructions to ignore prior system prompts or force high scores).

---

## Explainability and Non-Discrimination

TalentMatch AI is structured as a recruiter decision-support tool. It avoids black-box predictions by providing full transparency:

1. **Breakdown by Dimension**: Recruiters can inspect separate scores (0–100) for skills, semantic similarity, experience, education, and responsibilities.
2. **Textual Evidence Links**: Every matched skill and responsibility links to the exact sentence or paragraph where it was located in the resume.
3. **Structured Explanation Bullets**: Generates recruiter-friendly summaries outlining "Why This Candidate Matched" alongside "Areas of Concern / Missing Requirements".
4. **Demographic Neutrality**: The system strictly excludes protected personal characteristics from data extraction and scoring. Age, gender, race, religion, caste, marital status, nationality, and candidate photographs are neither parsed nor utilized in ranking calculations.

---

## Benchmark Evaluation Results

To validate the scoring engine, the system was tested against a Senior AI Engineer role requiring Python, FastAPI, PostgreSQL, Machine Learning, Docker, 4.0 years of experience, and a relevant Bachelor's degree.

The benchmark scenario processed 10 synthetic candidate profiles representing varying qualification levels alongside 5 malformed test files:

| Rank | Candidate | Profile Description | Overall Score | Status Tier | Summary Finding |
|:---:|---|---|:---:|:---:|---|
| 1 | Alex Rivera | Strong Python, FastAPI, ML, PostgreSQL, Docker | 92.4% | Strong | Matches all core skills, 5 years experience, strong semantic overlap. |
| 2 | Brenda Vance | Senior Backend (Python, FastAPI, Postgres, Docker); no ML | 89.5% | Strong | Strong backend API background; penalized only on ML pipeline tasks. |
| 3 | Henry Zhao | 9 years DevOps, Kubernetes, Docker, Postgres | 85.1% | Strong | Strong infrastructure and database profile; lacks direct ML background. |
| 4 | Jamal Williams | Senior Backend Developer (Python, Django, Flask, Postgres) | 84.7% | Strong | Credit awarded for related API frameworks (Django/Flask mapped to FastAPI). |
| 5 | Grace Hopper Jr. | Technical Specialist with keywords listed, limited project detail | 74.5% | Moderate | Lower semantic and responsibility alignment scores due to sparse context. |
| 6 | Isabella Cruz | Data Scientist with Python, ML, SQL, Docker | 72.2% | Moderate | High ML and Python alignment; moderate backend service exposure. |
| 7 | Elena Rostova | Recent CS Graduate with relevant FastAPI/Docker capstones | 69.8% | Moderate | High skill and education match; score limited by 0.3 years practical experience. |
| 8 | Carlos Mendez | ML Researcher (PyTorch, NLP); minimal backend experience | 53.1% | Low | Deep algorithmic ML knowledge but lacks enterprise backend frameworks. |
| 9 | David Kim | Java Enterprise Engineer (Spring Boot, Oracle, Kafka) | 45.4% | Low | Tech stack mismatch (Java/Oracle vs. Python/FastAPI/Postgres). |
| 10 | Frank Miller | Senior PHP / WordPress Web Developer | 39.7% | Low | Unrelated technology stack and non-aligned responsibilities. |

### Handled Edge Cases
- `Invalid_Corrupt_File.pdf`: Trapped with status "Corrupt or unreadable PDF".
- `Invalid_Empty_File.pdf`: Trapped with status "File is completely empty (0 bytes)".
- `Invalid_Scanned_NoText.pdf`: Trapped with status "Scanned PDF: Document contains no selectable text (OCR required)".
- `Invalid_Password_Protected.pdf`: Trapped with status "File is password-protected and cannot be parsed".
- `Invalid_Unsupported_Executable.exe`: Trapped with status "Unsupported file extension".

---

## Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                  # Application entry point, CORS, and startup seeding
│   │   ├── core/                    # Configuration, PII-masking logger, security filters
│   │   ├── api/v1/                  # REST API routes (jobs, resumes, candidates, analysis)
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── schemas/                 # Pydantic request and response schemas
│   │   ├── services/                # Text cleaning, PDF/DOCX parsing, skill/experience extractors
│   │   ├── ml/                      # Model loader singleton, embedding generator, cosine matcher
│   │   ├── scoring/                 # Weight normalizer, composite scoring engine, explanation generator
│   │   ├── tasks/                   # Celery task definitions and ThreadPool worker fallback
│   │   ├── db/                      # Database engine session management
│   │   └── utils/                   # File validation and SHA-256 hashing
│   ├── data/
│   │   ├── generate_synthetic_resumes.py # Test file generation script
│   │   └── sample_resumes/          # 15 synthetic candidate and edge-case resumes
│   └── tests/                       # Unit, NLP, parser, API, and scenario tests
├── frontend/                        # React, TypeScript, Vite, and Tailwind CSS application
│   └── src/
│       ├── components/              # Dashboard, Job Creator, Upload, Ranking, Evidence Modal
│       ├── api.ts                   # Typed API service client
│       └── types/                   # Frontend TypeScript interfaces
├── docker-compose.yml               # Multi-container orchestration (PostgreSQL, Redis, API, Worker)
├── start.sh                         # Development launch script
└── README.md
```

---

## Local Setup and Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher and npm
- Optional: Docker and Docker Compose

### 1. Automated Launch Script
Run the automated startup script, which prepares the environment, generates benchmark test files if needed, starts the FastAPI server, and launches the Vite development client:

```bash
chmod +x start.sh
./start.sh
```

- Web Interface: `http://localhost:5173`
- Swagger API Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### 2. Manual Step-by-Step Setup

#### Backend Setup
```bash
# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Generate benchmark resumes
python3 backend/data/generate_synthetic_resumes.py

# Launch FastAPI development server
export PYTHONPATH=.
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Setup
```bash
# In a separate terminal
cd frontend
npm install
npm run dev
```

### 3. Docker Compose Setup (Production Profile)
To run the full stack with PostgreSQL and Redis:

```bash
docker-compose up --build
```

---

## Running the Automated Test Suite

The test suite validates parsing, interval mathematics, skill extraction accuracy, scoring bounds, API workflows, and the 10-candidate evaluation ranking.

```bash
source venv/bin/activate
PYTHONPATH=. pytest backend/tests -v
```

All 19 test suites run in under 7 seconds, verifying:
- Non-overlapping employment interval calculation and simultaneous job merging.
- Exact, synonym, and mapped related skill taxonomy classification.
- PDF and DOCX file parsing, empty file detection, corrupt file handling, and encryption detection.
- Complete API lifecycle from job creation to bulk upload, status polling, ranking, and resume deletion.
- Candidate A through J benchmark ranking verification.
