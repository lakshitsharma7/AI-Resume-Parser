import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import docx
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("d:/AI resume/AI-Resume-Parser/test_resumes")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

# -------------------------------------------------------------
# 1. Simple One-Page Resume (.pdf)
# -------------------------------------------------------------
def generate_01_simple_one_page():
    pdf_path = OUTPUT_DIR / "01_simple_one_page.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    story.append(Paragraph("<b>Alex Mercer</b>", title_style))
    story.append(Paragraph("Austin, TX | alex.mercer@example.com | +1 512-555-0188<br/>https://linkedin.com/in/alexmercer | https://github.com/alexmercer", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", h2_style))
    story.append(Paragraph("Software Engineer with 3 years of experience in backend development and cloud architecture. Passionate about building high-performance microservices using Python and Go.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>WORK EXPERIENCE</b>", h2_style))
    story.append(Paragraph("<b>Software Engineer | Apex Systems | 2021-06 to Present</b>", body_style))
    story.append(Paragraph("• Architected RESTful microservices in FastAPI and PostgreSQL.<br/>• Integrated Redis cache layers cutting response times by 40%.<br/>• Automated CI/CD deployments using Docker and GitHub Actions.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Junior Developer | CodeCraft Studio | 2020-01 to 2021-05</b>", body_style))
    story.append(Paragraph("• Maintained Django REST APIs and PostgreSQL schemas.<br/>• Developed responsive user interfaces using React and TypeScript.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>EDUCATION</b>", h2_style))
    story.append(Paragraph("<b>Bachelor of Science in Computer Science | 2016 - 2020</b><br/>University of Texas at Austin", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", h2_style))
    story.append(Paragraph("• Languages: Python, Go, TypeScript, SQL, JavaScript<br/>• Frameworks: FastAPI, Django, React, Next.js<br/>• Databases: PostgreSQL, SQLite, Redis<br/>• Tools & Cloud: Docker, Kubernetes, AWS, Git, Linux", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>PROJECTS</b>", h2_style))
    story.append(Paragraph("<b>StreamSync | Python, WebSockets | https://github.com/alexmercer/streamsync</b><br/>Real-time data streaming server handling 20k concurrent WebSocket connections.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>CERTIFICATIONS</b>", h2_style))
    story.append(Paragraph("• AWS Certified Solutions Architect (2022)", body_style))

    doc.build(story)
    print("Generated 01_simple_one_page.pdf")

# -------------------------------------------------------------
# 2. Two-Column Layout Resume (.pdf)
# -------------------------------------------------------------
def generate_02_two_column_layout():
    pdf_path = OUTPUT_DIR / "02_two_column_layout.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    
    # Left sidebar background
    c.setFillColor(colors.HexColor("#F1F5F9"))
    c.rect(0, 0, 200, 792, fill=True, stroke=False)

    # Left Column (Contact & Skills)
    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, 750, "CONTACT")
    
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    c.drawString(20, 730, "Liam Gallagher")
    c.drawString(20, 715, "liam.g@example.com")
    c.drawString(20, 700, "+1 415-555-0199")
    c.drawString(20, 685, "San Francisco, CA")
    c.drawString(20, 670, "linkedin.com/in/liamg")
    c.drawString(20, 655, "github.com/liamg")

    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, 615, "TECHNICAL SKILLS")

    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    skills = [
        "Python", "TypeScript", "JavaScript",
        "React", "Next.js", "FastAPI",
        "PostgreSQL", "Redis", "MongoDB",
        "Docker", "AWS", "Git"
    ]
    y = 595
    for s in skills:
        c.drawString(20, y, f"• {s}")
        y -= 16

    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, y - 20, "EDUCATION")
    y -= 40
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "B.Tech in Computer Science")
    c.setFont("Helvetica", 8)
    c.drawString(20, y - 14, "UC Berkeley (2019)")

    # Right Column (Header, Summary, Experience)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(220, 750, "Liam Gallagher")
    c.setFont("Helvetica", 11)
    c.drawString(220, 732, "Senior Full Stack Engineer")

    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(220, 695, "PROFESSIONAL SUMMARY")
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    c.drawString(220, 678, "Results-oriented engineer with 4.5 years of experience delivering scalable web")
    c.drawString(220, 664, "applications and robust backend microservices.")

    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(220, 630, "WORK EXPERIENCE")

    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(220, 610, "Senior Software Engineer | Nova Labs | 2022-03 to Present")
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    c.drawString(230, 594, "• Engineered REST microservices using FastAPI and PostgreSQL.")
    c.drawString(230, 580, "• Led migration to React and Next.js frontend with Tailwind CSS.")
    c.drawString(230, 566, "• Containerized microservices with Docker and deployed onto AWS.")

    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(220, 536, "Software Developer | ByteWorks | 2019-08 to 2022-02")
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    c.drawString(230, 520, "• Developed backend APIs using Python and Django.")
    c.drawString(230, 506, "• Designed responsive client interfaces in React and Redux.")

    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(220, 470, "PROJECTS")
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(220, 452, "DocuParser | FastAPI, React | https://github.com/liamg/docuparser")
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 9)
    c.drawString(230, 436, "• Open source document processing pipeline with 1,200 GitHub stars.")

    c.save()
    print("Generated 02_two_column_layout.pdf")

# -------------------------------------------------------------
# 3. Multi-Page Resume (.pdf)
# -------------------------------------------------------------
def generate_03_multipage_resume():
    pdf_path = OUTPUT_DIR / "03_multipage_resume.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = []

    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    # Page 1
    story.append(Paragraph("<b>Marcus Vance</b>", title_style))
    story.append(Paragraph("New York, NY | marcus.vance@example.com | +1 212-555-0147<br/>https://linkedin.com/in/marcusvance | https://github.com/marcusvance", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", h2_style))
    story.append(Paragraph("Principal Engineering Leader with 8+ years of engineering experience architecting distributed cloud systems, high-frequency data pipelines, and leading engineering teams across North America.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>WORK EXPERIENCE</b>", h2_style))
    story.append(Paragraph("<b>Lead Architect | Global Cloud Corp | 2021-04 to Present</b>", body_style))
    story.append(Paragraph("• Directed architectural transformation to event-driven microservices on AWS.<br/>• Mentored team of 18 backend engineers across 3 squads.<br/>• Reduced platform infrastructure costs by $1.2M annually via container optimization.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Senior Software Engineer | DataStream Labs | 2018-06 to 2021-03</b>", body_style))
    story.append(Paragraph("• Built real-time stream ingestion pipelines in Python, Kafka, and Redis.<br/>• Handled over 150 million events per day with 99.99% service availability.<br/>• Designed automated test suites using PyTest and Docker.", body_style))

    # Page Break to Page 2
    story.append(PageBreak())

    story.append(Paragraph("<b>WORK EXPERIENCE (CONTINUED)</b>", h2_style))
    story.append(Paragraph("<b>Software Engineer | Apex FinTech | 2016-01 to 2018-05</b>", body_style))
    story.append(Paragraph("• Implemented core financial transaction APIs using Python, Django, and PostgreSQL.<br/>• Enforced strict SOC2 compliance, HMAC authentication, and encrypted data storage.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Junior Developer | Venture Studio | 2014-06 to 2015-12</b>", body_style))
    story.append(Paragraph("• Developed full stack web applications using Python, JavaScript, and MySQL.<br/>• Collaborated with product designers to ship 6 client web applications.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>EDUCATION</b>", h2_style))
    story.append(Paragraph("<b>Master of Science in Software Engineering | 2012 - 2014</b><br/>Columbia University, New York", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Bachelor of Science in Computer Engineering | 2008 - 2012</b><br/>New York University", body_style))

    # Page Break to Page 3
    story.append(PageBreak())

    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", h2_style))
    story.append(Paragraph("• Languages: Python, Go, Java, TypeScript, SQL<br/>• Frameworks: FastAPI, Django, Flask, Spring Boot, React<br/>• Databases: PostgreSQL, Redis, MongoDB, Elasticsearch, Cassandra<br/>• Cloud & DevOps: AWS, Kubernetes, Docker, Terraform, CI/CD, Linux", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROJECTS</b>", h2_style))
    story.append(Paragraph("<b>EventBus Core | Python, Kafka, Redis | https://github.com/marcusvance/eventbus</b><br/>High-throughput distributed event broker library with zero external daemon dependencies.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>CERTIFICATIONS</b>", h2_style))
    story.append(Paragraph("• AWS Certified Solutions Architect – Professional (2023)<br/>• Certified Kubernetes Administrator (CKA) (2022)", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>LANGUAGES</b>", h2_style))
    story.append(Paragraph("• English (Fluent), French (Professional)", body_style))

    doc.build(story)
    print("Generated 03_multipage_resume.pdf")

# -------------------------------------------------------------
# 4. Scanned / Image-Based Resume (.pdf)
# -------------------------------------------------------------
def generate_04_scanned_image_resume():
    # Render an image containing resume text, then embed it into a PDF
    img = Image.new('RGB', (1200, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((80, 80), "ELENA ROSTOVA", fill=(20, 40, 100))
    draw.text((80, 120), "Chicago, IL | elena.rostova@example.com | +1 312-555-0177", fill=(50, 50, 50))
    draw.text((80, 145), "https://linkedin.com/in/elenarostova | https://github.com/elenarostova", fill=(50, 50, 50))

    draw.text((80, 200), "PROFESSIONAL SUMMARY", fill=(20, 40, 100))
    draw.text((80, 230), "Data Engineer with 3 years experience building ETL pipelines in Python and SQL.", fill=(50, 50, 50))

    draw.text((80, 290), "EXPERIENCE", fill=(20, 40, 100))
    draw.text((80, 320), "Data Engineer | Metro Analytics | 2021-05 to Present", fill=(20, 20, 20))
    draw.text((80, 345), "- Engineered streaming pipelines using Python, PostgreSQL, and Redis.", fill=(50, 50, 50))
    draw.text((80, 370), "- Containerized data ingestion workloads with Docker.", fill=(50, 50, 50))

    draw.text((80, 430), "EDUCATION", fill=(20, 40, 100))
    draw.text((80, 460), "Bachelor of Science in Information Systems | 2017 - 2021", fill=(20, 20, 20))
    draw.text((80, 485), "University of Illinois at Chicago", fill=(50, 50, 50))

    draw.text((80, 540), "SKILLS", fill=(20, 40, 100))
    draw.text((80, 570), "Python, SQL, PostgreSQL, Docker, AWS, Git", fill=(50, 50, 50))

    img_path = OUTPUT_DIR / "04_scanned_image_resume.png"
    img.save(img_path)

    pdf_path = OUTPUT_DIR / "04_scanned_image_resume.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawImage(str(img_path), 0, 0, width=612, height=792)
    c.save()
    print("Generated 04_scanned_image_resume.pdf")

# -------------------------------------------------------------
# 5. Standard Word (.docx) Resume
# -------------------------------------------------------------
def generate_05_standard_word():
    docx_path = OUTPUT_DIR / "05_standard_word.docx"
    doc = docx.Document()

    h1 = doc.add_heading("Rachel Adams", level=0)
    p_contact = doc.add_paragraph("Seattle, WA | rachel.adams@example.com | +1 206-555-0162\nhttps://linkedin.com/in/racheladams | https://github.com/racheladams")

    doc.add_heading("PROFESSIONAL SUMMARY", level=1)
    doc.add_paragraph("DevOps & Cloud Engineer with 4 years of experience specializing in Kubernetes, Terraform, AWS, and CI/CD automation.")

    doc.add_heading("WORK EXPERIENCE", level=1)
    doc.add_paragraph("Senior DevOps Engineer | CloudNative Corp | 2022-01 to Present", style='List Bullet')
    doc.add_paragraph("Managed 15 multi-region Kubernetes clusters on AWS using Terraform and Helm.")
    doc.add_paragraph("Reduced build deployment latency by 65% with GitHub Actions CI/CD workflows.")

    doc.add_paragraph("Cloud Infrastructure Engineer | ScaleOps | 2020-03 to 2021-12", style='List Bullet')
    doc.add_paragraph("Automated server provisioning across AWS using Ansible and Python scripts.")

    doc.add_heading("EDUCATION", level=1)
    doc.add_paragraph("Bachelor of Science in Computer Science | 2016 - 2020\nUniversity of Washington")

    doc.add_heading("TECHNICAL SKILLS", level=1)
    doc.add_paragraph("Languages: Python, Bash, Go, SQL\nCloud & Tools: AWS, Docker, Kubernetes, Terraform, Ansible, Linux, Git")

    doc.add_heading("CERTIFICATIONS", level=1)
    doc.add_paragraph("AWS Certified DevOps Engineer – Professional (2022)")

    doc.save(str(docx_path))
    print("Generated 05_standard_word.docx")

# -------------------------------------------------------------
# 6. Overlapping Companies Resume (.pdf)
# -------------------------------------------------------------
def generate_06_overlapping_companies():
    pdf_path = OUTPUT_DIR / "06_overlapping_companies.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    story.append(Paragraph("<b>Julian Rivera</b>", title_style))
    story.append(Paragraph("Miami, FL | julian.rivera@example.com | +1 305-555-0133<br/>https://linkedin.com/in/julianrivera | https://github.com/julianrivera", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", h2_style))
    story.append(Paragraph("Full Stack Software Engineer with concurrent consulting and enterprise experience.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>WORK EXPERIENCE</b>", h2_style))
    # Job 1: 2021-01 to 2022-12 (24 months)
    story.append(Paragraph("<b>Lead Engineer | Enterprise Tech | 2021-01 to 2022-12</b>", body_style))
    story.append(Paragraph("• Architected enterprise web solutions in Python and Django.", body_style))
    story.append(Spacer(1, 6))

    # Job 2: 2021-06 to 2023-06 (Overlapping with Job 1! Total elapsed calendar time is 2021-01 to 2023-06 = 30 months = 2.5 years)
    story.append(Paragraph("<b>Senior Consultant | Freelance Digital | 2021-06 to 2023-06</b>", body_style))
    story.append(Paragraph("• Advised startup clients on FastAPI architecture and PostgreSQL optimizations.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>EDUCATION</b>", h2_style))
    story.append(Paragraph("<b>Bachelor of Science in Information Technology | 2017 - 2021</b><br/>University of Miami", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", h2_style))
    story.append(Paragraph("Python, Django, FastAPI, PostgreSQL, Redis, React, Docker, Git", body_style))

    doc.build(story)
    print("Generated 06_overlapping_companies.pdf")

# -------------------------------------------------------------
# 7. Incomplete Data Resume (.pdf)
# -------------------------------------------------------------
def generate_07_incomplete_data():
    pdf_path = OUTPUT_DIR / "07_incomplete_data.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

    # Missing Phone, Missing Location, Missing Summary, Missing Degree!
    story.append(Paragraph("<b>Devon Brooks</b>", title_style))
    story.append(Paragraph("devon.brooks@example.com<br/>https://github.com/devonbrooks", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>WORK EXPERIENCE</b>", h2_style))
    story.append(Paragraph("<b>Software Engineer | Solo Tech | 2022-01 to Present</b>", body_style))
    story.append(Paragraph("• Built backend services in Python and SQLite.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", h2_style))
    story.append(Paragraph("Python, SQLite, Git", body_style))

    doc.build(story)
    print("Generated 07_incomplete_data.pdf")

# -------------------------------------------------------------
# 8. Tables and Complex Formatting Resume (.pdf)
# -------------------------------------------------------------
def generate_08_tables_and_formatting():
    pdf_path = OUTPUT_DIR / "08_tables_and_formatting.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    title_style = ParagraphStyle('TStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BStyle', parent=styles['Normal'], fontSize=9, leading=12)

    story.append(Paragraph("<b>Samantha Reed</b>", title_style))
    story.append(Paragraph("Boston, MA | samantha.reed@example.com | +1 617-555-0192<br/>https://linkedin.com/in/samanthareed | https://github.com/samanthareed", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", h2_style))
    story.append(Paragraph("Senior Database Administrator and Cloud Architect with over 5 years of enterprise database experience.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>EMPLOYMENT HISTORY (TABLE FORMAT)</b>", h2_style))
    job_table_data = [
        ["Role", "Employer", "Dates", "Key Responsibilities"],
        ["Senior DBA", "Boston Financial", "2021-03 to Present", "Managed 40+ PostgreSQL and MySQL clusters on AWS RDS with 99.999% uptime."],
        ["Database Engineer", "DataCorp", "2019-01 to 2021-02", "Automated DB failover scripts in Python and optimized SQL queries."]
    ]
    t1 = Table(job_table_data, colWidths=[110, 100, 110, 220])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>EDUCATION & CREDENTIALS</b>", h2_style))
    edu_table_data = [
        ["Degree", "Institution", "Year", "CGPA / Details"],
        ["Bachelor of Science in Computer Science", "Boston University", "2019", "3.9 / 4.0 GPA"]
    ]
    t2 = Table(edu_table_data, colWidths=[180, 160, 60, 140])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>TECHNICAL COMPETENCIES</b>", h2_style))
    story.append(Paragraph("• Databases: PostgreSQL, MySQL, Redis, MongoDB, Oracle<br/>• Languages: SQL, Python, Bash<br/>• Cloud: AWS, Docker, Linux, Terraform, Git", body_style))

    doc.build(story)
    print("Generated 08_tables_and_formatting.pdf")

if __name__ == "__main__":
    generate_01_simple_one_page()
    generate_02_two_column_layout()
    generate_03_multipage_resume()
    generate_04_scanned_image_resume()
    generate_05_standard_word()
    generate_06_overlapping_companies()
    generate_07_incomplete_data()
    generate_08_tables_and_formatting()
    print("All 8 test resumes successfully created!")

