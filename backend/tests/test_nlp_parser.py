import pytest
from app.services.nlp_parser import NLPResumeParser
from app.services.skill_taxonomy import extract_and_categorize_skills

SAMPLE_RESUME_TEXT = """
Sarah Jenkins
San Francisco, CA | sarah.jenkins@example.com | +1 (555) 234-5678
https://linkedin.com/in/sarahjenkins | https://github.com/sarahjenkins

PROFESSIONAL SUMMARY
Senior Full Stack Engineer with over 4 years of experience architecting high-throughput distributed backend services and responsive web applications. Expert in Python, TypeScript, and cloud-native architecture.

WORK EXPERIENCE
Senior Software Engineer | Acme Corp | Mar 2022 – Present
- Designed microservices with FastAPI and PostgreSQL, serving 500k daily active users.
- Led migration of frontend from legacy React to Next.js and Tailwind CSS.
- Automated deployment pipelines using Docker and GitHub Actions.

Software Developer | Beta Innovations | Jan 2020 – Feb 2022
- Built RESTful APIs using Python, Django, and SQLite.
- Developed real-time analytics dashboards using React, Redux, and Node.js.

EDUCATION
Bachelor of Technology in Computer Science | 2016 – 2020
University of California, Berkeley

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, TypeScript, SQL, Go
- Frameworks: React, Next.js, FastAPI, Django
- Databases: PostgreSQL, SQLite, Redis, MongoDB
- Cloud & DevOps: AWS, Docker, Kubernetes, Linux, Git

PROJECTS
Cloud Task Orchestrator | FastAPI, Celery, Redis | https://github.com/sarahjenkins/orchestrator
Engineered an asynchronous task distribution pipeline handling 10,000 jobs per minute.

CERTIFICATIONS
AWS Certified Solutions Architect – Associate (2023)
"""

def test_nlp_personal_info_extraction():
    parsed = NLPResumeParser.parse(SAMPLE_RESUME_TEXT)
    personal = parsed["personal_information"]
    
    assert personal["full_name"] == "Sarah Jenkins"
    assert personal["email"] == "sarah.jenkins@example.com"
    assert "555" in personal["phone"]
    assert "San Francisco" in personal["location"]
    assert personal["linkedin"] == "https://linkedin.com/in/sarahjenkins"
    assert personal["github"] == "https://github.com/sarahjenkins"
    assert personal["confidence"]["email"] == 1.0

def test_nlp_experience_extraction():
    parsed = NLPResumeParser.parse(SAMPLE_RESUME_TEXT)
    prof = parsed["professional_information"]
    history = prof["employment_history"]
    
    assert len(history) >= 2
    assert any("Acme" in job["company_name"] for job in history)
    assert any("Beta" in job["company_name"] for job in history)
    assert prof["total_experience_years"] >= 4.0

def test_skills_taxonomy_and_boundaries():
    skills = extract_and_categorize_skills(SAMPLE_RESUME_TEXT)
    
    # Check languages
    assert "Python" in skills["programming_languages"]
    assert "TypeScript" in skills["programming_languages"]
    assert "Go" in skills["programming_languages"]
    assert "SQL" in skills["programming_languages"]
    
    # Verify no false-positive single letter tokens like 'C'
    # ("C" shouldn't match simply because words like "California" or "Computer" exist)
    assert "C" not in skills["programming_languages"]
    
    # Check frameworks
    assert "FastAPI" in skills["frameworks"]
    assert "React" in skills["frameworks"]
    assert "Django" in skills["frameworks"]
    assert "Next.js" in skills["frameworks"]
    
    # Check databases
    assert "PostgreSQL" in skills["databases"]
    assert "SQLite" in skills["databases"]
    assert "Redis" in skills["databases"]

def test_nlp_education_and_projects():
    parsed = NLPResumeParser.parse(SAMPLE_RESUME_TEXT)
    edu = parsed["education"]
    proj = parsed["projects"]
    certs = parsed["certifications"]
    
    assert len(edu) >= 1
    assert any("Bachelor" in e["degree"] or "B.Tech" in e["degree"] for e in edu)
    
    assert len(proj) >= 1
    assert any("Cloud Task Orchestrator" in p["title"] for p in proj)
    
    assert len(certs) >= 1
    assert any("AWS" in c["name"] for c in certs)

