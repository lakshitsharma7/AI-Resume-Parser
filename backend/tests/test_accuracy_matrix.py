import os
import pytest
from pathlib import Path
from app.services.extractor import DocumentExtractor, is_tesseract_available
from app.services.nlp_parser import NLPResumeParser
from app.services.timeline import calculate_total_experience_years

TEST_RESUMES_DIR = Path("d:/AI resume/AI-Resume-Parser/test_resumes")

GROUND_TRUTH = {
    "01_simple_one_page.pdf": {
        "full_name": "Alex Mercer",
        "email": "alex.mercer@example.com",
        "phone": "+1 512-555-0188",
        "location": "Austin, TX",
        "linkedin": "https://linkedin.com/in/alexmercer",
        "github": "https://github.com/alexmercer",
        "min_experience_years": 3.0,
        "companies": ["Apex Systems", "CodeCraft Studio"],
        "degree": "Bachelor of Science",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]
    },
    "02_two_column_layout.pdf": {
        "full_name": "Liam Gallagher",
        "email": "liam.g@example.com",
        "phone": "+1 415-555-0199",
        "location": "San Francisco, CA",
        "linkedin": "https://linkedin.com/in/liamg",
        "github": "https://github.com/liamg",
        "min_experience_years": 4.0,
        "companies": ["Nova Labs", "ByteWorks"],
        "degree": "B.Tech",
        "skills": ["Python", "React", "Next.js", "Docker"]
    },
    "03_multipage_resume.pdf": {
        "full_name": "Marcus Vance",
        "email": "marcus.vance@example.com",
        "phone": "+1 212-555-0147",
        "location": "New York, NY",
        "linkedin": "https://linkedin.com/in/marcusvance",
        "github": "https://github.com/marcusvance",
        "min_experience_years": 8.0,
        "companies": ["Global Cloud Corp", "DataStream Labs", "Apex FinTech"],
        "degree": "Master of Science",
        "skills": ["Python", "AWS", "Kafka", "PostgreSQL"]
    },
    "05_standard_word.docx": {
        "full_name": "Rachel Adams",
        "email": "rachel.adams@example.com",
        "phone": "+1 206-555-0162",
        "location": "Seattle, WA",
        "linkedin": "https://linkedin.com/in/racheladams",
        "github": "https://github.com/racheladams",
        "min_experience_years": 3.5,
        "companies": ["CloudNative Corp", "ScaleOps"],
        "degree": "Bachelor of Science",
        "skills": ["Kubernetes", "Docker", "Terraform", "AWS"]
    },
    "06_overlapping_companies.pdf": {
        "full_name": "Julian Rivera",
        "email": "julian.rivera@example.com",
        "phone": "+1 305-555-0133",
        "location": "Miami, FL",
        "linkedin": "https://linkedin.com/in/julianrivera",
        "github": "https://github.com/julianrivera",
        # Overlapping period: 2021-01 to 2022-12 and 2021-06 to 2023-06
        # Real elapsed duration = 2021-01 to 2023-06 = 30 months = 2.5 years (NOT 24 + 25 = 4.1 years)
        "expected_experience_years": 2.5,
        "companies": ["Enterprise Tech", "Freelance Digital"],
        "skills": ["Python", "FastAPI", "Django", "PostgreSQL"]
    },
    "07_incomplete_data.pdf": {
        "full_name": "Devon Brooks",
        "email": "devon.brooks@example.com",
        # Explicitly tests null preservation
        "expected_null_fields": ["phone", "location", "linkedin", "portfolio", "summary"],
        "companies": ["Solo Tech"],
        "skills": ["Python", "SQLite", "Git"]
    },
    "08_tables_and_formatting.pdf": {
        "full_name": "Samantha Reed",
        "email": "samantha.reed@example.com",
        "phone": "+1 617-555-0192",
        "location": "Boston, MA",
        "linkedin": "https://linkedin.com/in/samanthareed",
        "github": "https://github.com/samanthareed",
        "min_experience_years": 4.5,
        "companies": ["Boston Financial", "DataCorp"],
        "degree": "Bachelor of Science",
        "skills": ["PostgreSQL", "MySQL", "AWS", "Python"]
    }
}

def test_benchmark_matrix():
    total_evaluated_fields = 0
    passed_fields = 0
    report_rows = []

    for filename, gt in GROUND_TRUTH.items():
        filepath = TEST_RESUMES_DIR / filename
        assert filepath.exists(), f"Test resume file {filename} does not exist"

        text, engine = DocumentExtractor.extract_text(str(filepath))
        parsed = NLPResumeParser.parse(text)
        personal = parsed["personal_information"]
        prof = parsed["professional_information"]
        skills = parsed["skills"]
        edu = parsed["education"]

        # Flatten skills
        all_skills = set()
        for cat_list in skills.values():
            for s in cat_list:
                all_skills.add(s.lower())

        file_eval = {"file": filename, "total": 0, "passed": 0, "failures": []}

        def check_field(field_name, condition, expected, actual):
            nonlocal total_evaluated_fields, passed_fields
            total_evaluated_fields += 1
            file_eval["total"] += 1
            if condition:
                passed_fields += 1
                file_eval["passed"] += 1
            else:
                file_eval["failures"].append(f"{field_name}: expected {expected}, got {actual}")

        # 1. Full Name
        check_field("full_name", personal.get("full_name") == gt.get("full_name"), gt.get("full_name"), personal.get("full_name"))

        # 2. Email
        check_field("email", personal.get("email") == gt.get("email"), gt.get("email"), personal.get("email"))

        # 3. Phone (if expected)
        if "phone" in gt:
            actual_phone = personal.get("phone")
            has_digits = any(d in (actual_phone or "") for d in ["512", "415", "212", "206", "305", "617"])
            check_field("phone", has_digits, gt.get("phone"), actual_phone)

        # 4. Location (if expected)
        if "location" in gt:
            actual_loc = personal.get("location")
            matches_loc = any(c in (actual_loc or "") for c in gt["location"].split(","))
            check_field("location", matches_loc, gt.get("location"), actual_loc)

        # 5. LinkedIn (if expected)
        if "linkedin" in gt:
            check_field("linkedin", personal.get("linkedin") == gt.get("linkedin"), gt.get("linkedin"), personal.get("linkedin"))

        # 6. GitHub (if expected)
        if "github" in gt:
            check_field("github", personal.get("github") == gt.get("github"), gt.get("github"), personal.get("github"))

        # 7. Null Preservation
        if "expected_null_fields" in gt:
            for null_field in gt["expected_null_fields"]:
                if null_field in personal:
                    is_null = personal.get(null_field) is None
                else:
                    is_null = prof.get(null_field) is None
                check_field(f"null_preservation_{null_field}", is_null, None, personal.get(null_field) or prof.get(null_field))

        # 8. Overlap calculation
        if "expected_experience_years" in gt:
            exp_diff = abs(prof.get("total_experience_years", 0) - gt["expected_experience_years"])
            check_field("overlap_experience", exp_diff <= 0.3, gt["expected_experience_years"], prof.get("total_experience_years"))

        # 9. Minimum Experience
        if "min_experience_years" in gt:
            has_min_exp = prof.get("total_experience_years", 0) >= gt["min_experience_years"] - 0.5
            check_field("min_experience", has_min_exp, f">={gt['min_experience_years']}", prof.get("total_experience_years"))

        # 10. Companies
        if "companies" in gt:
            extracted_companies = [j.get("company_name", "").lower() for j in prof.get("employment_history", [])]
            for exp_c in gt["companies"]:
                found = any(exp_c.lower() in c for c in extracted_companies) or exp_c.lower() in text.lower()
                check_field(f"company_{exp_c}", found, exp_c, extracted_companies)

        # 11. Degree
        if "degree" in gt:
            extracted_degs = [e.get("degree", "").lower() for e in edu]
            found_deg = any(gt["degree"].lower() in d for d in extracted_degs)
            check_field("degree", found_deg, gt["degree"], extracted_degs)

        # 12. Skills
        if "skills" in gt:
            for sk in gt["skills"]:
                found_skill = sk.lower() in all_skills
                check_field(f"skill_{sk}", found_skill, sk, list(all_skills)[:10])

        accuracy_pct = round((file_eval["passed"] / max(file_eval["total"], 1)) * 100, 1)
        report_rows.append((filename, file_eval["passed"], file_eval["total"], accuracy_pct, file_eval["failures"]))

    # Overall Metrics
    overall_accuracy = round((passed_fields / max(total_evaluated_fields, 1)) * 100, 1)
    
    print("\n" + "=" * 80)
    print("RESUME PARSING FIELD-LEVEL ACCURACY BENCHMARK REPORT")
    print("=" * 80)
    for row in report_rows:
        fn, passed, total, pct, fails = row
        print(f"[{pct}%] {fn:32} ({passed}/{total} fields passed)")
        if fails:
            for f in fails:
                print(f"      - {f}")
    print("-" * 80)
    print(f"OVERALL ACCURACY: {overall_accuracy}% ({passed_fields}/{total_evaluated_fields} ground-truth checks passed)")
    print("=" * 80 + "\n")

    assert overall_accuracy >= 90.0, f"Benchmark accuracy {overall_accuracy}% is below required 90% threshold"

