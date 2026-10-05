import html
from pathlib import Path

import streamlit as st

from modules.resume_parser import extract_text
from modules.matcher import calculate_match, compare_skills
from modules.llm_analyzer import analyze_resume_with_llm
from modules.report_generator import generate_pdf_report


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)


# --------------------------------------------------
# LOAD CUSTOM CSS
# --------------------------------------------------

CSS_PATH = Path(__file__).parent / "assets" / "style.css"

try:
    with open(CSS_PATH, "r", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )
except FileNotFoundError:
    st.warning("Custom stylesheet not found. The app will use default styling.")


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "resume_version" not in st.session_state:
    st.session_state.resume_version = 0

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None

if "ai_generated" not in st.session_state:
    st.session_state.ai_generated = False


# --------------------------------------------------
# CLEAR ANALYSIS RESULTS
# --------------------------------------------------

def clear_analysis_results():
    st.session_state.analysis_results = None
    st.session_state.ai_feedback = None
    st.session_state.ai_generated = False


# --------------------------------------------------
# RESET APP
# --------------------------------------------------

def reset_app():
    st.session_state.resume_version += 1
    st.session_state.job_description = ""
    st.session_state.analysis_results = None
    st.session_state.ai_feedback = None
    st.session_state.ai_generated = False


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📄 AI Resume Analyzer")

st.write(
    "Analyze your resume against a job description "
    "using Machine Learning and AI."
)

st.divider()


# --------------------------------------------------
# RESUME AND JOB DESCRIPTION INPUT
# --------------------------------------------------

st.markdown("## Analyze Your Resume")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### Upload Your Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume in PDF format",
        type=["pdf"],
        key=f"resume_uploader_{st.session_state.resume_version}",
        on_change=clear_analysis_results,
    )

with col2:
    st.markdown("### Job Description")

    job_description = st.text_area(
        "Paste the job description here",
        placeholder="Paste the complete job description...",
        height=250,
        key="job_description",
        on_change=clear_analysis_results,
    )


# --------------------------------------------------
# ANALYZE RESUME
# --------------------------------------------------

if st.button("Analyze Resume", type="primary"):
    clear_analysis_results()

    if uploaded_file is None:
        st.error("Please upload your resume first.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:
        try:
            # --------------------------------------
            # EXTRACT RESUME TEXT
            # --------------------------------------

            with st.spinner("Extracting resume text..."):
                resume_text = extract_text(uploaded_file)

            if not resume_text or not resume_text.strip():
                st.error(
                    "No readable text found in the PDF. "
                    "Please upload a text-based PDF."
                )

            else:
                # ----------------------------------
                # TRADITIONAL ML ANALYSIS
                # ----------------------------------

                with st.spinner("Analyzing your resume..."):
                    match_score = calculate_match(
                        resume_text,
                        job_description,
                    )

                    matched, missing = compare_skills(
                        resume_text,
                        job_description,
                    )

                    total_skills = len(matched) + len(missing)

                    if total_skills > 0:
                        skill_percentage = (
                            len(matched) / total_skills
                        ) * 100
                    else:
                        skill_percentage = 0

                # ----------------------------------
                # SAVE RESULTS
                # ----------------------------------

                st.session_state.analysis_results = {
                    "match_score": match_score,
                    "matched": matched,
                    "missing": missing,
                    "skill_percentage": skill_percentage,
                    "resume_text": resume_text,
                    "job_description": job_description,
                }

        except Exception as e:
            st.error(f"Analysis failed: {e}")


# --------------------------------------------------
# DISPLAY ANALYSIS RESULTS
# --------------------------------------------------

results = st.session_state.analysis_results

if results is not None:
    match_score = results["match_score"]
    matched = results["matched"]
    missing = results["missing"]
    skill_percentage = results["skill_percentage"]

    # ----------------------------------------------
    # RESUME ANALYSIS DASHBOARD
    # ----------------------------------------------

    st.divider()
    st.header("Resume Analysis")

    col1, col2 = st.columns(2, gap="large")

    # ----------------------------------------------
    # OVERALL RESUME MATCH
    # ----------------------------------------------

    with col1:
        st.markdown(
            f"""
            <div class="score-card">
                <p class="score-title">Overall Resume Match</p>
                <h2 class="score-value">{match_score:.2f}%</h2>
                <p class="score-description">
                    Resume relevance to the job description
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(min(max(match_score / 100, 0.0), 1.0))

    # ----------------------------------------------
    # SKILL MATCH
    # ----------------------------------------------

    with col2:
        st.markdown(
            f"""
            <div class="score-card">
                <p class="score-title">Skill Match</p>
                <h2 class="score-value">{skill_percentage:.2f}%</h2>
                <p class="score-description">
                    Required skills found in your resume
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(min(max(skill_percentage / 100, 0.0), 1.0))

    # ----------------------------------------------
    # SKILLS COMPARISON
    # ----------------------------------------------

    st.divider()
    st.subheader("Skills Comparison")

    col1, col2 = st.columns(2, gap="large")

    # ----------------------------------------------
    # MATCHED SKILLS CARD
    # ----------------------------------------------

    with col1:
        matched_items = ""

        for skill in matched:
            safe_skill = html.escape(str(skill))
            matched_items += f"""
                <div class="skill-item matched-item">
                    <span class="skill-dot matched-dot"></span>
                    <span>{safe_skill}</span>
                </div>
            """

        if not matched:
            matched_items = """
                <p class="empty-skills">No matched skills found.</p>
            """

        st.html(
            f"""
            <div class="skills-card matched-card">
                <div class="skills-heading">
                    <span>✓ Matched Skills</span>
                    <span class="skill-count matched-count">
                        {len(matched)}
                    </span>
                </div>
                {matched_items}
            </div>
            """,
        )

    # ----------------------------------------------
    # MISSING SKILLS CARD
    # ----------------------------------------------

    with col2:
        missing_items = ""

        for skill in missing:
            safe_skill = html.escape(str(skill))
            missing_items += f"""
                <div class="skill-item missing-item">
                    <span class="skill-dot missing-dot"></span>
                    <span>{safe_skill}</span>
                </div>
            """

        if not missing:
            missing_items = """
                <p class="empty-skills">No missing skills found.</p>
            """

        st.html(
            f"""
            <div class="skills-card missing-card">
                <div class="skills-heading">
                    <span>! Missing Skills</span>
                    <span class="skill-count missing-count">
                        {len(missing)}
                    </span>
                </div>
                {missing_items}
            </div>
            """,
        )

    # ----------------------------------------------
    # IMPROVEMENT SUGGESTIONS
    # ----------------------------------------------

    st.divider()
    st.subheader("Improvement Suggestions")

    if missing:
        st.write(
            "Consider improving or highlighting the following skills "
            "if you genuinely have experience with them:"
        )

        for skill in missing:
            st.write(f"- {skill}")
    else:
        st.success(
            "All skills identified in the job description "
            "were found in your resume."
        )

    # ----------------------------------------------
    # OPTIONAL AI ANALYSIS
    # ----------------------------------------------

    st.divider()
    st.header("AI-Powered Resume Feedback")

    st.write(
        "Generate personalized AI feedback using Groq "
        "only when you need it."
    )

    if not st.session_state.ai_generated:
        if st.button(
            "Generate AI Analysis",
            type="secondary",
            key="generate_ai_analysis",
        ):
            try:
                with st.spinner("Generating personalized AI feedback..."):
                    feedback = analyze_resume_with_llm(
                        results["resume_text"],
                        results["job_description"],
                        missing,
                    )

                if (
                    feedback
                    and not feedback.startswith(
                        (
                            "LLM analysis failed:",
                            "Groq API key is missing.",
                        )
                    )
                ):
                    st.session_state.ai_feedback = feedback
                    st.session_state.ai_generated = True
                    st.rerun()
                else:
                    st.error(
                        feedback
                        or "AI feedback is currently unavailable."
                    )

            except Exception as e:
                st.error(f"AI analysis failed: {e}")

    if st.session_state.ai_generated:
        st.markdown(st.session_state.ai_feedback)
    else:
        st.info(
            "AI analysis has not been generated. "
            "Your traditional ML results are available."
        )

    # ----------------------------------------------
    # PDF REPORT DOWNLOAD
    # ----------------------------------------------

    st.divider()
    st.subheader("Download Analysis Report")

    try:
        pdf_report = generate_pdf_report(
            match_score=match_score,
            matched_skills=matched,
            missing_skills=missing,
            skill_percentage=skill_percentage,
            ai_feedback=(
                st.session_state.ai_feedback
                if st.session_state.ai_generated
                else None
            ),
        )

        st.download_button(
            label="Download PDF Report",
            data=pdf_report,
            file_name="AI_Resume_Analysis_Report.pdf",
            mime="application/pdf",
            key="download_pdf_report",
        )

    except Exception as e:
        st.error(f"Could not generate the PDF report: {e}")


# --------------------------------------------------
# RESET
# --------------------------------------------------

st.divider()

st.button(
    "Reset",
    on_click=reset_app,
)
