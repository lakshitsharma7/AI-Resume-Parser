import logging
from typing import Dict, Any, List

from app.services.timeline import (
    calculate_total_experience_years,
    calculate_total_experience_months,
    calculate_employment_duration,
    normalize_date_string
)

logger = logging.getLogger(__name__)

class ResumeMerger:
    """
    Fuses deterministic extractions with local LLM extractions.
    Ensures strict grounding (anti-hallucination) by validating fields against raw text.
    """

    @classmethod
    def merge(cls, nlp_data: Dict[str, Any], llm_data: Dict[str, Any] = None, raw_text: str = "") -> Dict[str, Any]:
        """
        Merges deterministic nlp_data with optional llm_data.
        Deterministic regex facts (email, phone, links) always take precedence if present.
        Semantic descriptions and summary from LLM are integrated when validated.
        """
        if not llm_data:
            return nlp_data

        merged = dict(nlp_data)
        raw_lower = raw_text.lower()

        # 1. Personal Information Fusion
        p_nlp = nlp_data.get("personal_information", {})
        p_llm = llm_data.get("personal_information", {})

        # Email & Phone & Links are strictly from deterministic regex (100% precision)
        merged_personal = {
            "full_name": p_nlp.get("full_name"),
            "email": p_nlp.get("email"),
            "phone": p_nlp.get("phone"),
            "location": p_nlp.get("location") or p_llm.get("location"),
            "linkedin": p_nlp.get("linkedin") or p_llm.get("linkedin"),
            "github": p_nlp.get("github") or p_llm.get("github"),
            "portfolio": p_nlp.get("portfolio") or p_llm.get("portfolio"),
            "confidence": dict(p_nlp.get("confidence", {}))
        }

        # If deterministic missed the name, check LLM candidate name against raw text
        if not merged_personal["full_name"] and p_llm.get("full_name"):
            llm_name = p_llm["full_name"].strip()
            # Grounding check: must appear in the raw text
            if llm_name.lower() in raw_lower:
                merged_personal["full_name"] = llm_name
                merged_personal["confidence"]["full_name"] = 0.85

        merged["personal_information"] = merged_personal

        # 2. Professional Information Fusion
        prof_nlp = nlp_data.get("professional_information", {})
        prof_llm = llm_data.get("professional_information", {})

        summary = prof_llm.get("summary") or prof_nlp.get("summary")
        
        # Merge employment history
        merged_history = []
        llm_history = prof_llm.get("employment_history", [])
        
        if llm_history and isinstance(llm_history, list):
            for item in llm_history:
                company = item.get("company_name", "")
                title = item.get("job_title", "")
                
                # Grounding check: company or title must be verified in raw text
                if company and company.lower() in raw_lower:
                    start_d = normalize_date_string(item.get("start_date"))
                    end_d = normalize_date_string(item.get("end_date"))
                    dur_m, is_curr = calculate_employment_duration(start_d, end_d)
                    
                    merged_history.append({
                        "company": company,
                        "company_name": company,
                        "designation": title or "Professional",
                        "job_title": title or "Professional",
                        "start_date": start_d,
                        "end_date": end_d,
                        "is_current": is_curr or item.get("is_current", False),
                        "duration_months": dur_m,
                        "responsibilities": item.get("responsibilities", ""),
                        "confidence_score": 0.90
                    })
        
        # Fall back to NLP history if LLM extracted empty or invalid history
        if not merged_history:
            merged_history = prof_nlp.get("employment_history", [])

        # Calculate overlap-free total experience
        total_exp_years = calculate_total_experience_years(merged_history)
        total_exp_months = calculate_total_experience_months(merged_history)

        curr_company = prof_nlp.get("current_company") or (merged_history[0].get("company_name") if merged_history else None)
        curr_title = prof_nlp.get("current_job_title") or (merged_history[0].get("job_title") if merged_history else None)

        merged["professional_information"] = {
            "summary": summary,
            "total_experience_years": total_exp_years,
            "total_experience_months": total_exp_months,
            "current_company": curr_company,
            "current_job_title": curr_title,
            "employment_history": merged_history
        }
        merged["professional_summary"] = summary
        merged["work_experience"] = merged_history
        merged["total_experience_years"] = total_exp_years
        merged["total_experience_months"] = total_exp_months

        # 3. Skills Fusion (Union of normalized skills)
        skills_nlp = nlp_data.get("skills", {})
        skills_llm = llm_data.get("skills", {})
        merged_skills = dict(skills_nlp)

        if isinstance(skills_llm, dict):
            for cat, s_list in skills_llm.items():
                if cat in merged_skills and isinstance(s_list, list):
                    existing_lower = {s.lower() for s in merged_skills[cat]}
                    for s in s_list:
                        # Grounding check: skill word must appear in raw text
                        if s and s.lower() in raw_lower and s.lower() not in existing_lower:
                            merged_skills[cat].append(s)
                            existing_lower.add(s.lower())

        merged["skills"] = merged_skills

        # 4. Education Fusion
        edu_nlp = nlp_data.get("education", [])
        edu_llm = llm_data.get("education", [])
        if edu_llm and isinstance(edu_llm, list):
            valid_llm_edu = []
            for e in edu_llm:
                deg = e.get("degree", "")
                inst = e.get("institution", "")
                if (deg and deg.lower() in raw_lower) or (inst and inst.lower() in raw_lower):
                    valid_llm_edu.append({
                        "degree": deg,
                        "institution": inst,
                        "university": e.get("university") or inst,
                        "specialization": e.get("specialization"),
                        "graduation_year": str(e.get("graduation_year", "")),
                        "score": str(e.get("score", "")) if e.get("score") else None,
                        "confidence_score": 0.90
                    })
            if valid_llm_edu:
                merged["education"] = valid_llm_edu
            else:
                merged["education"] = edu_nlp
        else:
            merged["education"] = edu_nlp

        # 5. Projects & Certifications
        if llm_data.get("projects") and isinstance(llm_data["projects"], list):
            valid_projs = []
            for p in llm_data["projects"]:
                title = p.get("title", "")
                if title and title.lower() in raw_lower:
                    valid_projs.append({
                        "title": title,
                        "description": p.get("description", ""),
                        "technologies": p.get("technologies", ""),
                        "link": p.get("link"),
                        "confidence_score": 0.88
                    })
            if valid_projs:
                merged["projects"] = valid_projs

        if llm_data.get("certifications") and isinstance(llm_data["certifications"], list):
            valid_certs = []
            for c in llm_data["certifications"]:
                name = c.get("name", "")
                if name and name.lower() in raw_lower:
                    valid_certs.append({
                        "name": name,
                        "issuer": c.get("issuer"),
                        "issue_date": str(c.get("issue_date", "")),
                        "confidence_score": 0.90
                    })
            if valid_certs:
                merged["certifications"] = valid_certs

        # Recalculate missing fields
        missing = []
        if not merged["personal_information"].get("full_name"):
            missing.append("full_name")
        if not merged["personal_information"].get("email"):
            missing.append("email")
        if not merged["personal_information"].get("phone"):
            missing.append("phone")
        if not merged["personal_information"].get("location"):
            missing.append("location")
        if not merged["personal_information"].get("linkedin"):
            missing.append("linkedin")
        if not merged["professional_information"].get("employment_history"):
            missing.append("employment_history")
        if not merged.get("education"):
            missing.append("education")
        if not merged["professional_information"].get("summary"):
            missing.append("summary")

        merged["missing_fields"] = missing
        return merged

