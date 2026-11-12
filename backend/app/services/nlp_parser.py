import re
import spacy
from typing import Dict, List, Any, Optional, Tuple

from app.services.skill_taxonomy import extract_and_categorize_skills
from app.services.timeline import (
    calculate_total_experience_years,
    calculate_total_experience_months,
    calculate_employment_duration,
    normalize_date_string
)

# Load spaCy English model safely
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Common header names to ignore when extracting names
NON_NAME_WORDS = {
    "resume", "curriculum", "vitae", "cv", "profile", "contact", "summary",
    "experience", "work", "education", "skills", "projects", "certifications",
    "developer", "engineer", "manager", "designer", "consultant", "analyst",
    "portfolio", "github", "linkedin", "email", "phone", "address", "page"
}

# Standard section markers
SECTION_PATTERNS = {
    "summary": re.compile(r'^(?:professional\s+summary|summary|profile|about\s+me|career\s+objective|objective)\b', re.IGNORECASE),
    "experience": re.compile(r'^(?:work\s+experience|professional\s+experience|experience|employment\s+history|work\s+history|employment)\b', re.IGNORECASE),
    "education": re.compile(r'^(?:education|academic\s+background|academics|qualifications|academic\s+history)\b', re.IGNORECASE),
    "skills": re.compile(r'^(?:technical\s+skills|skills|core\s+competencies|technologies|tech\s+stack|areas\s+of\s+expertise)\b', re.IGNORECASE),
    "projects": re.compile(r'^(?:projects|personal\s+projects|key\s+projects|academic\s+projects)\b', re.IGNORECASE),
    "certifications": re.compile(r'^(?:certifications|certificates|licenses|courses|accreditations)\b', re.IGNORECASE),
    "achievements": re.compile(r'^(?:achievements|awards|honors|extracurricular\s+activities|accomplishments)\b', re.IGNORECASE),
    "languages": re.compile(r'^(?:languages|languages\s+known|spoken\s+languages)\b', re.IGNORECASE)
}

DEGREE_TERMS = [
    r'b\.?tech(?:\s+in\s+[\w\s]+)?',
    r'b\.?e\.?(?:\s+in\s+[\w\s]+)?',
    r'b\.?s\.?c\.?',
    r'b\.?s\.?(?:\s+in\s+[\w\s]+)?',
    r'bachelor(?:\'s)?(?:\s+of\s+[\w\s]+)?',
    r'm\.?tech(?:\s+in\s+[\w\s]+)?',
    r'm\.?e\.?(?:\s+in\s+[\w\s]+)?',
    r'm\.?s\.?c\.?',
    r'm\.?s\.?(?:\s+in\s+[\w\s]+)?',
    r'master(?:\'s)?(?:\s+of\s+[\w\s]+)?',
    r'ph\.?d\.?',
    r'doctor\s+of\s+philosophy',
    r'bca\b', r'mca\b', r'bba\b', r'mba\b', r'b\.?com\b', r'm\.?com\b',
    r'diploma(?:\s+in\s+[\w\s]+)?', r'high\s+school', r'secondary\s+school'
]

COMMON_TITLES = [
    "software engineer", "senior software engineer", "full stack developer", "full stack engineer",
    "frontend developer", "backend developer", "web developer", "software developer",
    "lead developer", "technical lead", "engineering manager", "data scientist",
    "data engineer", "data analyst", "devops engineer", "cloud architect",
    "solutions architect", "system administrator", "qa engineer", "sdet",
    "product manager", "project manager", "consultant", "intern", "research assistant"
]

class NLPResumeParser:
    """
    Deterministic NLP & Heuristic Resume Parser.
    Extracts all candidate fields with grounding checks and confidence scores.
    """

    @classmethod
    def parse(cls, text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Personal Information
        personal_info = cls._extract_personal_info(text, lines)
        
        # 2. Section Partitioning
        sections = cls._partition_sections(lines)
        
        # 3. Professional Experience
        exp_data = cls._extract_experience(sections.get("experience", []), text)
        
        # 4. Skills Taxonomy Matching
        skills = extract_and_categorize_skills(text)
        
        # 5. Education
        education = cls._extract_education(sections.get("education", []), text)
        
        # 6. Projects
        projects = cls._extract_projects(sections.get("projects", []))
        
        # 7. Certifications
        certifications = cls._extract_certifications(sections.get("certifications", []))
        
        # 8. Additional Info
        achievements = cls._extract_list_items(sections.get("achievements", []))
        languages = cls._extract_languages(sections.get("languages", []), text)
        summary = cls._extract_summary(sections.get("summary", []), lines)

        # Calculate Total Experience
        total_exp_years = calculate_total_experience_years(exp_data.get("history", []))
        total_exp_months = calculate_total_experience_months(exp_data.get("history", []))

        # Check for missing fields
        missing_fields = []
        if not personal_info.get("full_name"):
            missing_fields.append("full_name")
        if not personal_info.get("email"):
            missing_fields.append("email")
        if not personal_info.get("phone"):
            missing_fields.append("phone")
        if not personal_info.get("location"):
            missing_fields.append("location")
        if not personal_info.get("linkedin"):
            missing_fields.append("linkedin")
        if not exp_data.get("history"):
            missing_fields.append("employment_history")
        if not education:
            missing_fields.append("education")
        if not summary:
            missing_fields.append("summary")

        # Overall confidence calculation
        conf_scores = list(personal_info.get("confidence", {}).values())
        if exp_data.get("history"):
            conf_scores.extend([job.get("confidence_score", 0.8) for job in exp_data["history"]])
        if education:
            conf_scores.extend([edu.get("confidence_score", 0.8) for edu in education])
        overall_conf = round(sum(conf_scores) / max(len(conf_scores), 1), 2) if conf_scores else 0.5

        # Field-level confidence and evidence dictionary
        p_evidence = personal_info.get("evidence", {})
        p_conf = personal_info.get("confidence", {})
        confidence_and_evidence = {
            "name": {"confidence": p_conf.get("full_name", 0.0), "evidence": p_evidence.get("full_name")},
            "email": {"confidence": p_conf.get("email", 0.0), "evidence": p_evidence.get("email")},
            "phone": {"confidence": p_conf.get("phone", 0.0), "evidence": p_evidence.get("phone")},
            "location": {"confidence": p_conf.get("location", 0.0), "evidence": p_evidence.get("location")},
            "linkedin": {"confidence": p_conf.get("linkedin", 0.0), "evidence": p_evidence.get("linkedin")},
            "github": {"confidence": p_conf.get("github", 0.0), "evidence": p_evidence.get("github")},
            "portfolio": {"confidence": p_conf.get("portfolio", 0.0), "evidence": p_evidence.get("portfolio")},
            "professional_summary": {"confidence": 0.90 if summary else 0.0, "evidence": summary[:140] if summary else None},
            "total_experience": {"confidence": 0.95 if total_exp_months > 0 else 0.0, "evidence": f"Overlap-free timeline: {total_exp_months} months across {len(exp_data.get('history', []))} positions"}
        }

        return {
            "personal_information": personal_info,
            "professional_summary": summary,
            "professional_information": {
                "summary": summary,
                "total_experience_years": total_exp_years,
                "total_experience_months": total_exp_months,
                "current_company": exp_data.get("current_company"),
                "current_job_title": exp_data.get("current_job_title"),
                "employment_history": exp_data.get("history", [])
            },
            "skills": skills,
            "work_experience": exp_data.get("history", []),
            "education": education,
            "projects": projects,
            "certifications": certifications,
            "internships": [],
            "achievements": achievements,
            "languages": languages,
            "total_experience_months": total_exp_months,
            "total_experience_years": total_exp_years,
            "confidence_and_evidence": confidence_and_evidence,
            "missing_fields": missing_fields,
            "overall_confidence": overall_conf
        }

    @classmethod
    def _extract_personal_info(cls, text: str, lines: List[str]) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "name": None,
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "github": None,
            "portfolio": None,
            "confidence": {},
            "evidence": {}
        }

        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        if email_match:
            val = email_match.group(0).strip().rstrip(".,")
            info["email"] = val
            info["confidence"]["email"] = 1.0
            info["evidence"]["email"] = email_match.group(0)
        else:
            info["confidence"]["email"] = 0.0

        # Phone Number
        phone_match = re.search(r'(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}', text)
        if phone_match:
            digits = re.sub(r'\D', '', phone_match.group(0))
            if 10 <= len(digits) <= 15:
                val = phone_match.group(0).strip().rstrip(".,")
                info["phone"] = val
                info["confidence"]["phone"] = 0.95
                info["evidence"]["phone"] = phone_match.group(0)
        if not info["phone"]:
            info["confidence"]["phone"] = 0.0

        # LinkedIn
        li_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_\-\/]+)', text, re.IGNORECASE)
        if li_match:
            info["linkedin"] = f"https://linkedin.com/in/{li_match.group(1).strip('/')}"
            info["confidence"]["linkedin"] = 1.0
            info["evidence"]["linkedin"] = li_match.group(0)
        else:
            info["confidence"]["linkedin"] = 0.0

        # GitHub
        gh_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_\-\/]+)', text, re.IGNORECASE)
        if gh_match:
            username = gh_match.group(1).strip('/')
            if username.lower() not in ["features", "explore", "about", "pricing"]:
                info["github"] = f"https://github.com/{username}"
                info["confidence"]["github"] = 1.0
                info["evidence"]["github"] = gh_match.group(0)
        if not info["github"]:
            info["confidence"]["github"] = 0.0

        # Portfolio URL
        port_match = re.search(r'(?:https?:\/\/)?([a-zA-Z0-9_-]+\.(?:dev|me|io|info|tech|app))(?:\/[^\s]*)?', text, re.IGNORECASE)
        if port_match:
            domain = port_match.group(0).strip().rstrip(".,")
            if "github" not in domain and "linkedin" not in domain:
                val = domain if domain.startswith("http") else f"https://{domain}"
                info["portfolio"] = val
                info["confidence"]["portfolio"] = 0.9
                info["evidence"]["portfolio"] = port_match.group(0)
        if not info["portfolio"]:
            info["confidence"]["portfolio"] = 0.0

        # Full Name
        cls._extract_name(lines, info)

        # Location
        cls._extract_location(lines, info)

        return info

    @classmethod
    def _extract_name(cls, lines: List[str], info: Dict[str, Any]):
        """Identifies the candidate name from top headers or spaCy NER."""
        # Top 4 lines heuristic
        for line in lines[:4]:
            clean = re.sub(r'[^\w\s]', '', line).strip()
            words = clean.split()
            # If 2 to 4 capitalized words and not in blacklisted header keywords
            if 2 <= len(words) <= 4:
                if not any(w.lower() in NON_NAME_WORDS for w in words):
                    if all(w[0].isupper() for w in words if w):
                        name_str = " ".join(words)
                        info["full_name"] = name_str
                        info["name"] = name_str
                        info["confidence"]["full_name"] = 0.88
                        info["evidence"]["full_name"] = line
                        info["evidence"]["name"] = line
                        return

        # Fallback to spaCy NER
        if nlp:
            header_text = "\n".join(lines[:6])
            doc = nlp(header_text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    clean = ent.text.strip()
                    words = clean.split()
                    if 2 <= len(words) <= 4 and not any(w.lower() in NON_NAME_WORDS for w in words):
                        info["full_name"] = clean
                        info["name"] = clean
                        info["confidence"]["full_name"] = 0.92
                        info["evidence"]["full_name"] = ent.text
                        info["evidence"]["name"] = ent.text
                        return

        info["confidence"]["full_name"] = 0.0

    @classmethod
    def _extract_location(cls, lines: List[str], info: Dict[str, Any]):
        """Extracts location (City, State, Country) from top contact lines or GPE entities."""
        loc_pattern = re.compile(r'\b([A-Z][a-zA-Z\s]+),\s*([A-Z]{2}|[A-Z][a-zA-Z\s]+)(?:,\s*([A-Z][a-zA-Z\s]+))?\b')
        for line in lines[:8]:
            m = loc_pattern.search(line)
            if m:
                matched_str = m.group(0).strip()
                # Ensure it doesn't match degree or University or Skills
                words_lower = [w.lower() for w in re.findall(r'\b\w+\b', matched_str)]
                tech_words = {"python", "sqlite", "sql", "java", "react", "git", "docker", "aws", "node", "linux", "html", "css"}
                if any(w in tech_words for w in words_lower):
                    continue
                if not any(d in matched_str.lower() for d in ["university", "bachelor", "master", "institute", "college", "school"]):
                    info["location"] = matched_str
                    info["confidence"]["location"] = 0.85
                    info["evidence"]["location"] = matched_str
                    return

        if nlp:
            header_text = "\n".join(lines[:8])
            doc = nlp(header_text)
            gpe_ents = [ent.text.strip() for ent in doc.ents if ent.label_ == "GPE"]
            if gpe_ents:
                loc_val = ", ".join(gpe_ents[:2])
                info["location"] = loc_val
                info["confidence"]["location"] = 0.80
                info["evidence"]["location"] = loc_val
                return

        info["confidence"]["location"] = 0.0

    @classmethod
    def _partition_sections(cls, lines: List[str]) -> Dict[str, List[str]]:
        """Partitions resume lines into discrete sections based on recognized headers."""
        sections: Dict[str, List[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            clean_line = line.strip().rstrip(":")
            found_sec = None
            for sec_name, pattern in SECTION_PATTERNS.items():
                if pattern.match(clean_line) and len(clean_line.split()) <= 4:
                    found_sec = sec_name
                    break

            if found_sec:
                current_section = found_sec
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections.setdefault(current_section, []).append(line)

        return sections

    @classmethod
    def _extract_summary(cls, summary_lines: List[str], all_lines: List[str]) -> Optional[str]:
        if summary_lines:
            text = " ".join([l.strip() for l in summary_lines if l.strip()])
            if len(text) > 30:
                return text
        return None

    @classmethod
    def _extract_experience(cls, exp_lines: List[str], full_text: str) -> Dict[str, Any]:
        """Extracts individual employment records with dates, titles, and companies."""
        history = []
        current_job: Dict[str, Any] = {}
        date_pattern = re.compile(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}[-/]\d{1,2}|\d{1,2}[-/]\d{4}|\d{4})\s*(?:-|–|—|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4}[-/]\d{1,2}|\d{1,2}[-/]\d{4}|\d{4}|Present|Current|Till date)',
            re.IGNORECASE
        )

        for line in exp_lines:
            date_match = date_pattern.search(line)
            if date_match:
                if current_job.get("company_name") or current_job.get("job_title"):
                    history.append(current_job)
                
                start_str = date_match.group(1)
                end_str = date_match.group(2)
                duration_m, is_curr = calculate_employment_duration(start_str, end_str)

                # Split remainder of line for company/title
                line_without_dates = line.replace(date_match.group(0), "").strip(" |-–—,")
                parts = [p.strip() for p in re.split(r'[-–—|@,]', line_without_dates) if p.strip()]

                title = "Software Engineer"
                company = "Company"
                if len(parts) >= 2:
                    title, company = parts[0], parts[1]
                elif len(parts) == 1:
                    company = parts[0]

                current_job = {
                    "company": company,
                    "company_name": company,
                    "designation": title,
                    "job_title": title,
                    "start_date": normalize_date_string(start_str),
                    "end_date": normalize_date_string(end_str),
                    "is_current": is_curr,
                    "duration_months": duration_m,
                    "responsibilities": "",
                    "confidence_score": 0.88
                }
            else:
                if current_job:
                    # Accumulate responsibilities
                    clean = line.strip(" •-*")
                    if clean:
                        if current_job["responsibilities"]:
                            current_job["responsibilities"] += "\n" + clean
                        else:
                            current_job["responsibilities"] = clean

        if current_job.get("company_name") or current_job.get("job_title"):
            history.append(current_job)

        # Identify current company and title
        current_company = None
        current_title = None
        for job in history:
            if job.get("is_current") or "present" in str(job.get("end_date", "")).lower():
                current_company = job.get("company_name")
                current_title = job.get("job_title")
                break
        if not current_company and history:
            current_company = history[0].get("company_name")
            current_title = history[0].get("job_title")

        return {
            "current_company": current_company,
            "current_job_title": current_title,
            "history": history
        }

    @classmethod
    def _extract_education(cls, edu_lines: List[str], full_text: str) -> List[Dict[str, Any]]:
        education = []
        combined_edu = "\n".join(edu_lines) if edu_lines else full_text

        # Search degree matches
        for deg_pat in DEGREE_TERMS:
            matches = list(re.finditer(deg_pat, combined_edu, re.IGNORECASE))
            for m in matches:
                degree_text = m.group(0).strip()
                # Find year near the match
                start_window = max(0, m.start() - 100)
                end_window = min(len(combined_edu), m.end() + 150)
                window_text = combined_edu[start_window:end_window]
                
                # Search for year range or single year
                year_range_match = re.search(r'\b(19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(19\d{2}|20\d{2})\b', window_text)
                if year_range_match:
                    start_yr = year_range_match.group(1)
                    end_yr = year_range_match.group(2)
                else:
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', window_text)
                    start_yr = None
                    end_yr = year_match.group(1) if year_match else None

                # Find specialization field: "in <field>"
                field_match = re.search(r'\bin\s+([A-Za-z\s]+?)(?:\||\n|,|\d|\(|$)', degree_text, re.IGNORECASE)
                field_name = field_match.group(1).strip() if field_match else None

                # Find institution / university in window
                inst_match = re.search(r'(?:at|from|,)?\s*([A-Z][a-zA-Z\s]+(?:University|College|Institute|School|Academy)[a-zA-Z\s]*)', window_text)
                institution = inst_match.group(1).strip() if inst_match else None

                education.append({
                    "degree": degree_text.title(),
                    "institution": institution,
                    "university": institution,
                    "field": field_name,
                    "specialization": field_name,
                    "start_year": start_yr,
                    "end_year": end_yr,
                    "graduation_year": end_yr,
                    "score": None,
                    "confidence_score": 0.85
                })

        # Deduplicate degrees
        unique_edu = []
        seen_degrees = set()
        for item in education:
            key = (item["degree"].lower(), item["graduation_year"])
            if key not in seen_degrees:
                seen_degrees.add(key)
                unique_edu.append(item)

        return unique_edu

    @classmethod
    def _extract_projects(cls, proj_lines: List[str]) -> List[Dict[str, Any]]:
        projects = []
        current_proj: Dict[str, Any] = {}

        for line in proj_lines:
            clean = line.strip(" •-*")
            if not clean:
                continue

            # Check if this line looks like a project title
            is_title = False
            parts = [p.strip() for p in clean.split("|")]
            if len(parts) >= 2 and len(parts[0].split()) <= 8:
                is_title = True
            elif len(clean.split()) <= 8 and (clean.isupper() or clean.istitle() or ":" in clean):
                is_title = True

            if is_title:
                if current_proj.get("title"):
                    projects.append(current_proj)
                title = parts[0].strip().rstrip(":")
                tech = parts[1].strip() if len(parts) > 1 else None
                link = None
                for part in parts[1:]:
                    link_m = re.search(r'https?://[^\s]+', part)
                    if link_m:
                        link = link_m.group(0)
                        break
                current_proj = {
                    "name": title,
                    "title": title,
                    "description": "",
                    "technologies": tech,
                    "link": link,
                    "confidence_score": 0.85
                }
            else:
                if current_proj:
                    # Check for link
                    link_m = re.search(r'https?://[^\s]+', clean)
                    if link_m:
                        current_proj["link"] = link_m.group(0)
                    if current_proj["description"]:
                        current_proj["description"] += "\n" + clean
                    else:
                        current_proj["description"] = clean

        if current_proj.get("title"):
            projects.append(current_proj)

        return projects

    @classmethod
    def _extract_certifications(cls, cert_lines: List[str]) -> List[Dict[str, Any]]:
        certs = []
        for line in cert_lines:
            clean = line.strip(" •-*")
            if clean and len(clean) > 4:
                # Find year if present
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', clean)
                year = year_match.group(1) if year_match else None
                name = clean
                if year:
                    name = re.sub(r'[\(\[\-,\s]*\b' + year + r'\b[\)\]]*', '', clean).strip()

                certs.append({
                    "name": name,
                    "issuer": None,
                    "issue_date": year,
                    "confidence_score": 0.90
                })
        return certs

    @classmethod
    def _extract_list_items(cls, lines: List[str]) -> List[str]:
        items = []
        for line in lines:
            clean = line.strip(" •-*")
            if clean and len(clean) > 5:
                items.append(clean)
        return items

    @classmethod
    def _extract_languages(cls, lang_lines: List[str], full_text: str) -> List[str]:
        standard_langs = ["English", "Spanish", "French", "German", "Hindi", "Mandarin", "Japanese", "Arabic", "Portuguese", "Russian", "Italian"]
        found = []
        source_text = "\n".join(lang_lines) if lang_lines else full_text
        for lang in standard_langs:
            if re.search(rf'\b{lang}\b', source_text, re.IGNORECASE):
                found.append(lang)
        return found
