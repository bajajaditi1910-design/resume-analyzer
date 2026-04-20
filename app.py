import streamlit as st
from PyPDF2 import PdfReader
import re

st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("🚀 AI Resume Analyzer (Rule-Based)")
st.markdown("### 📄 Upload multiple resumes & compare with job description")

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF)", type="pdf", accept_multiple_files=True
)

jd = st.text_area("Paste Job Description")

skills_db = [
    "python", "java", "sql", "dbms", "react",
    "node", "javascript", "html", "css", "mongodb",
    "dsa"
]

skill_aliases = {
    "dsa": ["data structures", "algorithms", "data structures and algorithms"],
    "javascript": ["js"],
    "node": ["node.js", "nodejs"],
    "react": ["react.js", "reactjs"],
    "sql": ["mysql", "postgresql"]
}

display_names = {
    "react": "React.js",
    "node": "Node.js",
    "javascript": "JavaScript",
    "dsa": "DSA"
}

def format_skills(skill_list):
    return ", ".join([display_names.get(skill, skill.capitalize()) for skill in skill_list])

def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()

stopwords = [
    "we", "are", "for", "a", "the", "and", "with",
    "in", "of", "to", "is", "required",
    "software", "skills", "developer", "knowledge",
    "backend", "development", "looking", "need", "jobs"
]

if uploaded_files and jd:
    jd_text = jd.lower()

    jd_words = re.split(r"[,\s]+", jd_text)
    jd_words = [word.replace(".js", "").replace(".", "") for word in jd_words]

    jd_keywords = [
        word.strip()
        for word in jd_words
        if word and word not in stopwords
    ]

    jd_skills = [skill for skill in skills_db if skill in jd_keywords]

    results = []

    for file in uploaded_files:
        resume_text = extract_text(file)

        found_skills = []

        for skill in jd_skills:
            if skill in resume_text:
                found_skills.append(skill)
            elif skill in skill_aliases:
                for alias in skill_aliases[skill]:
                    if alias in resume_text:
                        found_skills.append(skill)
                        break

        missing_skills = [skill for skill in jd_skills if skill not in found_skills]

        score = int((len(found_skills) / len(jd_skills)) * 100) if jd_skills else 0

        results.append({
            "name": file.name,
            "score": score,
            "skills": found_skills,
            "missing": missing_skills
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    st.subheader("🏆 Resume Ranking")

    for i, res in enumerate(results):
        with st.container():
            st.markdown(f"### #{i+1} {res['name']}")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Match Score", f"{res['score']}%")

            with col2:
                st.metric("Skills Found", len(res["skills"]))

            st.success("✅ Skills Found:")
            st.write(format_skills(res["skills"]) if res["skills"] else "None")

            st.error("❌ Missing Skills:")
            st.write(format_skills(res["missing"]) if res["missing"] else "None")

            if res["missing"]:
                st.info(f"💡 Improve by adding: {format_skills(res['missing'])}")

            st.divider()