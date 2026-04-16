import streamlit as st
from PyPDF2 import PdfReader
import re

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("📄 Resume Analyzer")
st.markdown("### 🚀 Analyze resumes, match skills & rank candidates")
st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")
job_description = st.sidebar.text_area("📌 Paste Job Description")

# ---------------- SKILLS LIST ----------------
SKILLS_DB = [
    "python", "java", "sql", "react.js", "react", "machine learning",
    "data analysis", "c++", "javascript", "html", "css", "dsa"
]

# ---------------- FUNCTIONS ----------------

def extract_text(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()


def normalize_text(text):
    text = text.lower()
    text = text.replace("reactjs", "react.js")
    text = text.replace("react js", "react.js")
    return text


def extract_skills(text):
    text = normalize_text(text)
    found = set()

    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text):
            found.add(skill.lower())

    return list(found)


def calculate_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0
    matched = set(resume_skills) & set(jd_skills)
    return int((len(matched) / len(jd_skills)) * 100)


# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "📤 Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- PROCESS ----------------
if uploaded_files and job_description:

    jd_text = normalize_text(job_description)
    jd_skills = extract_skills(jd_text)

    results = []

    for file in uploaded_files:
        text = extract_text(file)
        skills = extract_skills(text)

        score = calculate_score(skills, jd_skills)
        missing = list(set(jd_skills) - set(skills))

        results.append({
            "name": file.name,
            "score": score,
            "skills": skills,
            "missing": missing
        })

    # SORT BY SCORE
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # ---------------- DISPLAY ----------------
    st.subheader("🏆 Resume Ranking")

    for i, res in enumerate(results):
        with st.container():
            st.markdown(f"### #{i+1} {res['name']}")

            col1, col2 = st.columns(2)

            with col1:
                # Color score
                if res["score"] > 80:
                    st.success(f"Match Score: {res['score']}%")
                elif res["score"] > 50:
                    st.warning(f"Match Score: {res['score']}%")
                else:
                    st.error(f"Match Score: {res['score']}%")

                # Progress bar
                st.progress(res["score"] / 100)

            with col2:
                st.metric("Skills Found", len(res["skills"]))

            # Skills Found
            st.success("✅ Skills Found:")
            st.write(", ".join(res["skills"]) if res["skills"] else "None")

            # Missing Skills
            st.error("❌ Missing Skills:")
            st.write(", ".join(res["missing"]) if res["missing"] else "None")

            # Suggested Skills
            suggested = list(set(SKILLS_DB) - set(res["skills"]) - set(res["missing"]))
            st.info(f"💡 Suggested Skills: {', '.join(suggested[:5])}")

            st.divider()

else:
    st.info("👈 Upload resumes and paste job description to start analysis")