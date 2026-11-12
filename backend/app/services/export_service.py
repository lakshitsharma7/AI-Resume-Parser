import io
from typing import Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExportService:
    """
    Generates structured multi-sheet Excel workbooks and formatted JSON candidate exports.
    """

    @classmethod
    def generate_excel(cls, candidate_data: Dict[str, Any]) -> io.BytesIO:
        """
        Creates a beautifully styled, multi-tab Excel spreadsheet from candidate data.
        """
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Styling constants
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        section_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        section_font = Font(name="Calibri", size=11, bold=True, color="0F172A")
        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=11)
        
        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        personal = candidate_data.get("personal_information", {})
        prof = candidate_data.get("professional_information", {})
        skills = candidate_data.get("skills", {})
        edu = candidate_data.get("education", [])
        projects = candidate_data.get("projects", [])
        certs = candidate_data.get("certifications", [])

        # ==========================================
        # 1. Sheet: Candidate Profile
        # ==========================================
        ws_prof = wb.create_sheet(title="Profile Summary")
        ws_prof.views.sheetView[0].showGridLines = True

        ws_prof.append(["Candidate Profile Overview", ""])
        ws_prof.merge_cells("A1:B1")
        ws_prof["A1"].font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
        ws_prof["A1"].fill = header_fill
        ws_prof["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws_prof.row_dimensions[1].height = 30

        overview_rows = [
            ("Full Name", personal.get("full_name") or "N/A"),
            ("Email", personal.get("email") or "N/A"),
            ("Phone", personal.get("phone") or "N/A"),
            ("Location", personal.get("location") or "N/A"),
            ("LinkedIn", personal.get("linkedin") or "N/A"),
            ("GitHub", personal.get("github") or "N/A"),
            ("Portfolio", personal.get("portfolio") or "N/A"),
            ("Current Job Title", prof.get("current_job_title") or "N/A"),
            ("Current Company", prof.get("current_company") or "N/A"),
            ("Total Experience (Years)", f"{prof.get('total_experience_years', 0.0)} yrs"),
            ("Overall Extraction Confidence", f"{round(candidate_data.get('overall_confidence', 0.0) * 100)}%"),
            ("Professional Summary", prof.get("summary") or "N/A")
        ]

        for label, val in overview_rows:
            ws_prof.append([label, val])
            curr_row = ws_prof.max_row
            ws_prof.cell(row=curr_row, column=1).font = bold_font
            ws_prof.cell(row=curr_row, column=1).fill = section_fill
            ws_prof.cell(row=curr_row, column=1).border = thin_border
            ws_prof.cell(row=curr_row, column=2).font = regular_font
            ws_prof.cell(row=curr_row, column=2).border = thin_border
            if label == "Professional Summary":
                ws_prof.cell(row=curr_row, column=2).alignment = Alignment(wrap_text=True)
                ws_prof.row_dimensions[curr_row].height = 45

        # ==========================================
        # 2. Sheet: Employment History
        # ==========================================
        ws_exp = wb.create_sheet(title="Work Experience")
        ws_exp.views.sheetView[0].showGridLines = True
        
        headers_exp = ["Company Name", "Job Title", "Start Date", "End Date", "Current?", "Duration (Months)", "Key Responsibilities"]
        ws_exp.append(headers_exp)
        for col_idx in range(1, len(headers_exp) + 1):
            cell = ws_exp.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws_exp.row_dimensions[1].height = 25

        history = prof.get("employment_history", [])
        for job in history:
            ws_exp.append([
                job.get("company_name", ""),
                job.get("job_title", ""),
                job.get("start_date", ""),
                job.get("end_date", ""),
                "Yes" if job.get("is_current") else "No",
                job.get("duration_months", 0),
                job.get("responsibilities", "")
            ])
            r = ws_exp.max_row
            for col_idx in range(1, len(headers_exp) + 1):
                c = ws_exp.cell(row=r, column=col_idx)
                c.font = regular_font
                c.border = thin_border
                if col_idx == 7:
                    c.alignment = Alignment(wrap_text=True)

        # ==========================================
        # 3. Sheet: Categorized Skills
        # ==========================================
        ws_skills = wb.create_sheet(title="Technical Skills")
        ws_skills.views.sheetView[0].showGridLines = True

        headers_skills = ["Category", "Skill Name"]
        ws_skills.append(headers_skills)
        for col_idx in range(1, 3):
            cell = ws_skills.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws_skills.row_dimensions[1].height = 25

        category_labels = {
            "programming_languages": "Programming Languages",
            "frameworks": "Frameworks",
            "libraries": "Libraries",
            "databases": "Databases",
            "cloud": "Cloud & DevOps",
            "ai_ml": "AI & Machine Learning",
            "tools": "Development Tools",
            "other_skills": "Other Competencies"
        }

        for cat_key, label in category_labels.items():
            cat_skills = skills.get(cat_key, [])
            for s in cat_skills:
                ws_skills.append([label, s])
                r = ws_skills.max_row
                ws_skills.cell(row=r, column=1).font = bold_font
                ws_skills.cell(row=r, column=1).border = thin_border
                ws_skills.cell(row=r, column=2).font = regular_font
                ws_skills.cell(row=r, column=2).border = thin_border

        # ==========================================
        # 4. Sheet: Education
        # ==========================================
        ws_edu = wb.create_sheet(title="Education")
        ws_edu.views.sheetView[0].showGridLines = True

        headers_edu = ["Degree", "Institution", "University", "Graduation Year", "Score"]
        ws_edu.append(headers_edu)
        for col_idx in range(1, len(headers_edu) + 1):
            cell = ws_edu.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws_edu.row_dimensions[1].height = 25

        for e in edu:
            ws_edu.append([
                e.get("degree", ""),
                e.get("institution", ""),
                e.get("university", ""),
                e.get("graduation_year", ""),
                e.get("score", "")
            ])
            r = ws_edu.max_row
            for col_idx in range(1, len(headers_edu) + 1):
                c = ws_edu.cell(row=r, column=col_idx)
                c.font = regular_font
                c.border = thin_border

        # ==========================================
        # 5. Sheet: Projects & Certifications
        # ==========================================
        ws_proj = wb.create_sheet(title="Projects & Certs")
        ws_proj.views.sheetView[0].showGridLines = True

        ws_proj.append(["Key Projects", "", "", ""])
        ws_proj.merge_cells("A1:D1")
        ws_proj["A1"].font = header_font
        ws_proj["A1"].fill = header_fill
        ws_proj["A1"].alignment = Alignment(horizontal="left", vertical="center")
        ws_proj.row_dimensions[1].height = 22

        headers_p = ["Project Title", "Technologies", "URL / Link", "Description"]
        ws_proj.append(headers_p)
        for col_idx in range(1, 5):
            c = ws_proj.cell(row=2, column=col_idx)
            c.font = bold_font
            c.fill = section_fill
            c.border = thin_border

        for p in projects:
            ws_proj.append([
                p.get("title", ""),
                p.get("technologies", ""),
                p.get("link", ""),
                p.get("description", "")
            ])
            r = ws_proj.max_row
            for col_idx in range(1, 5):
                c = ws_proj.cell(row=r, column=col_idx)
                c.font = regular_font
                c.border = thin_border

        # Spacer row
        ws_proj.append([])
        
        ws_proj.append(["Certifications & Credentials", "", "", ""])
        start_cert_head = ws_proj.max_row
        ws_proj.merge_cells(f"A{start_cert_head}:D{start_cert_head}")
        ws_proj[f"A{start_cert_head}"].font = header_font
        ws_proj[f"A{start_cert_head}"].fill = header_fill
        ws_proj[f"A{start_cert_head}"].alignment = Alignment(horizontal="left", vertical="center")
        ws_proj.row_dimensions[start_cert_head].height = 22

        ws_proj.append(["Certification Name", "Issuing Organization", "Issue Date", ""])
        sub_head = ws_proj.max_row
        for col_idx in range(1, 4):
            c = ws_proj.cell(row=sub_head, column=col_idx)
            c.font = bold_font
            c.fill = section_fill
            c.border = thin_border

        for cert in certs:
            ws_proj.append([
                cert.get("name", ""),
                cert.get("issuer", ""),
                cert.get("issue_date", "")
            ])
            r = ws_proj.max_row
            for col_idx in range(1, 4):
                c = ws_proj.cell(row=r, column=col_idx)
                c.font = regular_font
                c.border = thin_border

        # Auto-adjust column widths for all sheets
        for sheet in wb.worksheets:
            for col in sheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    val_str = str(cell.value or '')
                    # Limit width calculation if long description
                    if len(val_str) > max_len and len(val_str) < 60:
                        max_len = len(val_str)
                sheet.column_dimensions[col_letter].width = max(max_len + 4, 15)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream

