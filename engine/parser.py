import fitz
import re


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    text = ""

    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()

        return text

    except Exception as e:
        print("PDF Error:", e)
        return ""


def parse_resume_to_json(text, client=None):
    """Parse resume locally (NO API USED)"""

    # ------------------------
    # EMAIL
    # ------------------------
    email_match = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text
    )

    email = email_match[0] if email_match else ""

    # ------------------------
    # NAME (first line guess)
    # ------------------------
    lines = text.split("\n")
    name = lines[0].strip() if lines else "Unknown"

    # ------------------------
    # SKILLS DETECTION
    # ------------------------
    skills_db = [
        "python","java","c++","sql","machine learning","deep learning",
        "data science","pandas","numpy","tensorflow","pytorch",
        "opencv","html","css","javascript","react","node",
        "streamlit","flask","django","git","docker"
    ]

    skills_found = []

    for skill in skills_db:
        if skill.lower() in text.lower():
            skills_found.append(skill)

    # ------------------------
    # EXPERIENCE SECTION
    # ------------------------
    experience = ""

    if "experience" in text.lower():
        exp_start = text.lower().find("experience")
        experience = text[exp_start:exp_start+500]

    # ------------------------
    # PROJECT SECTION
    # ------------------------
    projects = ""

    if "project" in text.lower():
        proj_start = text.lower().find("project")
        projects = text[proj_start:proj_start+500]

    # ------------------------
    # FINAL JSON OUTPUT
    # ------------------------
    return {
        "name": name,
        "email": email,
        "skills": skills_found,
        "experience": experience,
        "projects": projects
    }