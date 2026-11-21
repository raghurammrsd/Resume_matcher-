import os
import pymupdf
import docx

DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_resumes")
os.makedirs(DATA_DIR, exist_ok=True)

# Candidate definitions matching the scenario
CANDIDATES = [
    {
        "filename": "Candidate_A_Alex_Rivera.pdf",
        "format": "pdf",
        "name": "Alex Rivera",
        "email": "alex.rivera@example.com",
        "phone": "+1-555-0101",
        "text": """Alex Rivera
Senior AI & Backend Engineer
Email: alex.rivera@example.com | Phone: +1-555-0101 | San Francisco, CA

PROFESSIONAL SUMMARY
Results-driven AI and Backend Engineer with 5 years of experience building scalable REST APIs, deploying machine learning pipelines, and containerizing distributed microservices with Docker and Kubernetes.

WORK EXPERIENCE
Senior Software Engineer | Apex Neural Tech
Jan 2022 - Present
- Architected and built high-performance production REST APIs using FastAPI, Python, and PostgreSQL handling 25M daily requests.
- Developed end-to-end machine learning pipelines using PyTorch and scikit-learn for automated document classification and predictive modeling.
- Containerized microservices using Docker and orchestrated multi-region deployments with Kubernetes and CI/CD pipelines.
- Optimized PostgreSQL queries and database schemas, reducing latency by 42%.

Backend & ML Engineer | DataFlow Systems
Jun 2019 - Dec 2021
- Developed scalable backend services in Python and FastAPI integrated with PostgreSQL.
- Implemented machine learning models for predictive maintenance, achieving 94% classification precision.
- Built automated Docker container workflows and deployed scalable API endpoints on AWS.

EDUCATION
B.Tech in Computer Science and Engineering | University of California, Berkeley
2015 - 2019

TECHNICAL SKILLS
Languages & Frameworks: Python, FastAPI, SQL, PyTorch, Scikit-learn
Databases & Cloud: PostgreSQL, Docker, Kubernetes, Redis, AWS
"""
    },
    {
        "filename": "Candidate_B_Brenda_Vance.docx",
        "format": "docx",
        "name": "Brenda Vance",
        "email": "brenda.vance@example.com",
        "phone": "+1-555-0102",
        "text": """Brenda Vance
Senior Backend Engineer
Email: brenda.vance@example.com | Phone: +1-555-0102

PROFESSIONAL SUMMARY
Senior Backend Engineer with 5 years of experience building resilient cloud services, microservices, and database systems. Strong expertise in Python, FastAPI, Docker, and PostgreSQL.

WORK EXPERIENCE
Lead Backend Engineer | CloudScale Networks
Jan 2021 - Present
- Built and maintained robust REST APIs using FastAPI and Python with PostgreSQL integration.
- Designed Docker container environments and continuous deployment pipelines.
- Architected database migration strategies and asynchronous task processing with Redis and Celery.
- Led backend engineering team of 6 engineers ensuring 99.99% service uptime.

Software Engineer | ServerLogic Corp
May 2019 - Dec 2020
- Developed backend microservices using Python and PostgreSQL.
- Containerized existing legacy workloads into lightweight Docker containers.
- Implemented comprehensive automated unit and integration tests.

EDUCATION
Bachelor of Science in Computer Science | University of Michigan
2015 - 2019

TECHNICAL SKILLS
Python, FastAPI, PostgreSQL, Docker, Redis, Celery, REST API, Git, Linux
"""
    },
    {
        "filename": "Candidate_C_Carlos_Mendez.pdf",
        "format": "pdf",
        "name": "Carlos Mendez",
        "email": "carlos.mendez@example.com",
        "phone": "+1-555-0103",
        "text": """Carlos Mendez
Machine Learning Specialist
Email: carlos.mendez@example.com | Phone: +1-555-0103

PROFESSIONAL SUMMARY
Applied Machine Learning Researcher and Data Scientist with 3 years of hands-on experience developing deep learning architectures and NLP algorithms in Python. Limited experience with enterprise backend frameworks.

WORK EXPERIENCE
Machine Learning Engineer | Cognition Labs
Aug 2023 - Present
- Researched and trained state-of-the-art transformer and natural language processing models using PyTorch and Python.
- Evaluated machine learning predictive performance and statistical models.
- Collaborated with research scientists to publish algorithmic benchmarks.

Junior Data Scientist | Visionary AI
Jun 2021 - Jul 2023
- Built predictive modeling prototypes using Python, scikit-learn, and Jupyter notebooks.
- Performed statistical feature engineering on large multi-modal tabular datasets.

EDUCATION
Master of Science in Artificial Intelligence | Stanford University
2019 - 2021
Bachelor of Science in Mathematics | UCLA
2015 - 2019

TECHNICAL SKILLS
Python, Machine Learning, PyTorch, Scikit-learn, NLP, Deep Learning, Statistics
"""
    },
    {
        "filename": "Candidate_D_David_Kim.pdf",
        "format": "pdf",
        "name": "David Kim",
        "email": "david.kim@example.com",
        "phone": "+1-555-0104",
        "text": """David Kim
Enterprise Java Developer
Email: david.kim@example.com | Phone: +1-555-0104

PROFESSIONAL SUMMARY
Software Engineer with 4 years of experience specializing in Java enterprise applications, Spring Boot microservices, and Oracle relational databases.

WORK EXPERIENCE
Java Software Engineer | FinTech Enterprise
Jan 2022 - Present
- Developed enterprise banking microservices using Core Java, Spring Boot, and Hibernate.
- Interfaced with Oracle SQL databases and Apache Kafka messaging streams.
- Maintained legacy SOAP and internal RESTful services.

Junior Java Programmer | Systems Global
Jul 2020 - Dec 2021
- Created backend batch processing jobs using Java and Maven.
- Wrote SQL queries and stored procedures in Oracle database.

EDUCATION
Bachelor of Science in Information Technology | Purdue University
2016 - 2020

TECHNICAL SKILLS
Java, Spring Boot, Hibernate, Oracle SQL, Apache Kafka, Maven, Jenkins
"""
    },
    {
        "filename": "Candidate_E_Elena_Rostova.pdf",
        "format": "pdf",
        "name": "Elena Rostova",
        "email": "elena.rostova@example.com",
        "phone": "+1-555-0105",
        "text": """Elena Rostova
Associate Software & AI Engineer (Fresh Graduate)
Email: elena.rostova@example.com | Phone: +1-555-0105

PROFESSIONAL SUMMARY
Recent Computer Science graduate with high honors. Completed rigorous academic and personal capstone projects building REST APIs with FastAPI, Python, PostgreSQL, and basic machine learning models.

ACADEMIC & INTERNSHIP EXPERIENCE
Software Engineering Intern | NextGen Startups
May 2025 - Aug 2025
- Built backend endpoints using Python and FastAPI with PostgreSQL database integration.
- Created Docker containers for local developer workflow environment.
- Integrated a machine learning sentiment analysis model into an internal dashboard.

Capstone AI Project | University
Sep 2024 - Apr 2025
- Developed an intelligent document summarizer using Python, FastAPI, and scikit-learn.
- Containerized the application with Docker and deployed it for university testing.

EDUCATION
Bachelor of Technology in Computer Science | Georgia Institute of Technology
Graduated May 2025 (GPA: 3.9/4.0)

TECHNICAL SKILLS
Python, FastAPI, PostgreSQL, Docker, Machine Learning, Scikit-learn, Git
"""
    },
    {
        "filename": "Candidate_F_Frank_Miller.docx",
        "format": "docx",
        "name": "Frank Miller",
        "email": "frank.miller@example.com",
        "phone": "+1-555-0106",
        "text": """Frank Miller
Senior Web Developer
Email: frank.miller@example.com | Phone: +1-555-0106

PROFESSIONAL SUMMARY
Experienced webmaster and PHP developer with 8 years of web development experience building CMS websites, WordPress themes, and PHP/MySQL applications.

WORK EXPERIENCE
Senior Web Developer | Creative Web Agency
Jan 2018 - Present
- Built custom WordPress themes and plugins using PHP, HTML5, CSS3, and jQuery.
- Configured Apache web servers and managed cPanel hosting environments.
- Maintained MySQL database tables and optimized web page load times.

Web Developer | Digital Press LLC
May 2016 - Dec 2017
- Developed responsive eCommerce websites using WooCommerce and PHP.

EDUCATION
Bachelor of Arts in Graphic Design and Web Communications
2012 - 2016

TECHNICAL SKILLS
PHP, WordPress, HTML, CSS, JavaScript, jQuery, MySQL, Apache, cPanel
"""
    },
    {
        "filename": "Candidate_G_Grace_Hopper_Jr.pdf",
        "format": "pdf",
        "name": "Grace Hopper Jr.",
        "email": "grace.hopper.jr@example.com",
        "phone": "+1-555-0107",
        "text": """Grace Hopper Jr.
Technical Specialist
Email: grace.hopper.jr@example.com | Phone: +1-555-0107

SKILLS LIST
Python, FastAPI, PostgreSQL, Docker, Machine Learning, AI

WORK EXPERIENCE
IT Consultant | Self-Employed
2023 - Present
- Worked on various client IT tasks and setup workstations.
- Provided technical guidance on software installations.

Junior Assistant | Tech Services
2021 - 2022
- Assisted in administrative technology tasks.

EDUCATION
B.S. in Computer Science | State College
2017 - 2021
"""
    },
    {
        "filename": "Candidate_H_Henry_Zhao.pdf",
        "format": "pdf",
        "name": "Henry Zhao",
        "email": "henry.zhao@example.com",
        "phone": "+1-555-0108",
        "text": """Henry Zhao
Lead Infrastructure Engineer
Email: henry.zhao@example.com | Phone: +1-555-0108

PROFESSIONAL SUMMARY
Staff DevOps and Cloud Infrastructure Architect with 9 years of experience managing large-scale Kubernetes clusters, multi-cloud networking, and terraform infrastructure. Limited direct experience in FastAPI application programming or machine learning.

WORK EXPERIENCE
Lead Infrastructure Architect | CloudSphere Inc
Jan 2020 - Present
- Deployed and operated 150+ production Kubernetes clusters running on AWS and GCP.
- Managed containerization standards with Docker and Podman across 300 microservices.
- Optimized PostgreSQL relational database failover topologies and replication.

Senior DevOps Engineer | InfraCore
Jun 2015 - Dec 2019
- Built CI/CD pipelines, automated Terraform scripts, and Linux server hardening.

EDUCATION
B.S. in Computer Engineering | University of Illinois Urbana-Champaign
2011 - 2015

TECHNICAL SKILLS
Docker, Kubernetes, PostgreSQL, Linux, Terraform, AWS, GCP, CI/CD, Git, Bash
"""
    },
    {
        "filename": "Candidate_I_Isabella_Cruz.pdf",
        "format": "pdf",
        "name": "Isabella Cruz",
        "email": "isabella.cruz@example.com",
        "phone": "+1-555-0109",
        "text": """Isabella Cruz
Data Scientist & ML Engineer
Email: isabella.cruz@example.com | Phone: +1-555-0109

PROFESSIONAL SUMMARY
Data Scientist with 4 years of experience building predictive models, statistical forecasting, and machine learning pipelines in Python. Experienced in SQL and analytical databases.

WORK EXPERIENCE
Data Scientist | Quant Analytics
Mar 2022 - Present
- Built machine learning and predictive modeling pipelines using Python, scikit-learn, and pandas.
- Wrote advanced PostgreSQL queries for large-scale customer behavioral modeling.
- Packaged ML training scripts into Docker containers for reproducible training runs.

Junior Data Analyst | MetricWorks
Jul 2020 - Feb 2022
- Extracted and cleaned multi-gigabyte datasets with SQL and Python.
- Trained regression models for marketing attribution.

EDUCATION
Master of Science in Data Science | New York University
2018 - 2020
B.S. in Statistics | Rutgers University
2014 - 2018

TECHNICAL SKILLS
Python, Machine Learning, Scikit-learn, PostgreSQL, SQL, Docker, Pandas, Statistics
"""
    },
    {
        "filename": "Candidate_J_Jamal_Williams.pdf",
        "format": "pdf",
        "name": "Jamal Williams",
        "email": "jamal.williams@example.com",
        "phone": "+1-555-0110",
        "text": """Jamal Williams
Senior Backend API Developer
Email: jamal.williams@example.com | Phone: +1-555-0110

PROFESSIONAL SUMMARY
Senior Backend Engineer with 5 years of experience developing REST APIs in Python (Django and Flask), managing PostgreSQL databases, and containerizing services with Docker.

WORK EXPERIENCE
Senior Backend Engineer | Apex Cloud Solutions
Jan 2021 - Present
- Designed high-throughput REST APIs using Python, Django REST Framework, and Flask.
- Maintained and optimized PostgreSQL database queries, indexes, and connection pooling.
- Containerized backend services with Docker and configured automated CI/CD testing.
- Integrated background task processing using Redis and Celery.

Backend Developer | WebWorks
Jun 2019 - Dec 2020
- Built RESTful web services in Python and Flask backed by PostgreSQL.
- Authored Dockerfiles and managed containerized staging environments.

EDUCATION
B.Tech in Computer Science | University of Texas at Austin
2015 - 2019

TECHNICAL SKILLS
Python, Django, Flask, PostgreSQL, Docker, REST API, Redis, Celery, Git, SQL
"""
    }
]

def create_pdf(filename: str, text: str):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842) # A4
    rect = pymupdf.Rect(50, 50, 545, 792)
    page.insert_textbox(rect, text, fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
    doc.save(os.path.join(DATA_DIR, filename))
    doc.close()

def create_docx(filename: str, text: str):
    doc = docx.Document()
    lines = text.strip().splitlines()
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.isupper() and len(line_s) < 30:
            doc.add_heading(line_s, level=2)
        elif line_s.startswith("- "):
            doc.add_paragraph(line_s[2:], style='List Bullet')
        else:
            doc.add_paragraph(line_s)
    doc.save(os.path.join(DATA_DIR, filename))

def create_invalid_resumes():
    # 1. Empty PDF (0 bytes)
    open(os.path.join(DATA_DIR, "Invalid_Empty_File.pdf"), "w").close()
    
    # 2. Corrupt PDF (garbage bytes)
    with open(os.path.join(DATA_DIR, "Invalid_Corrupt_File.pdf"), "wb") as f:
        f.write(b"%PDF-1.4\n%GARBAGE_BINARY_CORRUPTED_STREAM_XXXXXXX123456789")
        
    # 3. Scanned PDF (valid PDF structure but zero selectable text)
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    # Draw a rectangle mimicking an image, but no text inserted
    page.draw_rect(pymupdf.Rect(50, 50, 500, 700), color=(0.8, 0.8, 0.8), fill=(0.9, 0.9, 0.9))
    doc.save(os.path.join(DATA_DIR, "Invalid_Scanned_NoText.pdf"))
    doc.close()
    
    # 4. Password-protected PDF
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 72), "Confidential Resume Data")
    # Save with user password
    perm = int(
        pymupdf.PDF_PERM_ACCESSIBILITY
        | pymupdf.PDF_PERM_PRINT
        | pymupdf.PDF_PERM_COPY
        | pymupdf.PDF_PERM_ANNOTATE
    )
    doc.save(
        os.path.join(DATA_DIR, "Invalid_Password_Protected.pdf"),
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="secret123",
        user_pw="locked123",
        permissions=perm
    )
    doc.close()
    
    # 5. Unsupported file format
    with open(os.path.join(DATA_DIR, "Invalid_Unsupported_Executable.exe"), "wb") as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00BinaryMockExecutable")

def main():
    print("Generating 10 synthetic candidates (PDF & DOCX)...")
    for cand in CANDIDATES:
        if cand["format"] == "pdf":
            create_pdf(cand["filename"], cand["text"])
        else:
            create_docx(cand["filename"], cand["text"])
            
    print("Generating invalid test files (empty, corrupt, scanned, password-protected, unsupported)...")
    create_invalid_resumes()
    
    generated = os.listdir(DATA_DIR)
    print(f"Successfully generated {len(generated)} test resume files in {DATA_DIR}!")

if __name__ == "__main__":
    main()
