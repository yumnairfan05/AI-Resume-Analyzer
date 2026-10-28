
import html
from pathlib import Path

import streamlit as st

from src.analyzer import analyze, build_report
from src.parser import extract_text

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
CSS_FILE = ROOT / "assets" / "style.css"

if CSS_FILE.exists():
    st.markdown(
        f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner="Loading AI model...")
def warm_up():
    from src.matcher import load_model
    return load_model()


def chips(items, kind):
    if not items:
        return '<p class="empty">No skills to display.</p>'

    return "".join(
        f'<span class="chip {kind}">{html.escape(str(item))}</span>'
        for item in items
    )


def metric(label, value):
    if value is None:
        return (
            '<div class="metric">'
            '<b>n/a</b>'
            f'<small>{html.escape(label)}</small>'
            '</div>'
        )

    score = max(0, min(100, float(value)))

    return (
        '<div class="metric">'
        f'<b>{html.escape(str(value))}%</b>'
        f'<small>{html.escape(label)}</small>'
        f'<div class="bar"><i style="width:{score}%"></i></div>'
        '</div>'
    )


def show_home():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-content">
                <span class="hero-badge">✦ AI POWERED</span>
                <h1>Does your <span>CV</span> fit the job?</h1>
                <p>
                    Upload your CV, paste a job description, and get an
                    instant match score, identify missing skills, and
                    discover personalized suggestions to improve your profile.
                </p>
            </div>
            <div class="hero-art">
                <div class="art-glow"></div>
                <div class="art-document">
                    <div class="art-avatar">●</div>
                    <div class="art-line long"></div>
                    <div class="art-line medium"></div>
                    <div class="art-line short"></div>
                    <div class="art-line long"></div>
                </div>
                <div class="art-search">⌕</div>
                <span class="art-star star-one">✦</span>
                <span class="art-star star-two">✧</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="medium")

    with left:
        st.markdown(
            """
            <div class="input-heading">
                <div class="heading-icon">▤</div>
                <div>
                    <h3>Your CV</h3>
                    <p>Upload your resume in PDF, DOCX or TXT format.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cv_file = st.file_uploader(
            "Upload your CV",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
            key="resume_upload",
        )

        if cv_file:
            st.markdown(
                f"""
                <div class="file-status">
                    <span class="file-symbol">✓</span>
                    <div class="file-info">
                        <strong>{html.escape(cv_file.name)}</strong>
                        <small>{cv_file.size / 1024:.1f} KB · File selected</small>
                    </div>
                    <span class="file-check">✓</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            """
            <div class="input-heading">
                <div class="heading-icon purple">▣</div>
                <div>
                    <h3>Job Description</h3>
                    <p>Paste the job posting or key responsibilities here.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        jd_text = st.text_area(
            "Job description",
            height=175,
            max_chars=10000,
            label_visibility="collapsed",
            placeholder=(
                "e.g. We are looking for an AI/ML Intern with knowledge "
                "of Python, machine learning, data analysis and problem solving..."
            ),
            key="job_description",
        )

        st.markdown(
            f'<div class="character-count">{len(jd_text)} / 10000 characters</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="analyze-area">', unsafe_allow_html=True)
    go = st.button(
        "✦  Analyze My CV     →",
        type="primary",
        use_container_width=True,
        key="analyze_cv",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if go:
        if not cv_file:
            st.warning("Please upload your CV first.")
            st.stop()

        if len(jd_text.strip()) < 60:
            st.warning(
                "Please enter a complete job description "
                "with at least 60 characters."
            )
            st.stop()

        try:
            cv_text = extract_text(cv_file)

            if not cv_text or not cv_text.strip():
                st.error(
                    "No readable text was found in your CV. "
                    "Please try another file."
                )
                st.stop()

        except (ValueError, Exception) as error:
            st.error(f"Could not read the CV: {error}")
            st.stop()

        try:
            with st.spinner("Analyzing your CV and matching your skills..."):
                warm_up()
                st.session_state["result"] = analyze(cv_text, jd_text)

            st.session_state["analysis_complete"] = True

        except Exception as error:
            st.error(f"Analysis failed: {error}")
            st.stop()

    result = st.session_state.get("result")

    if result:
        st.markdown(
            '<div class="results-heading">'
            '<span class="hero-badge">✦ ANALYSIS COMPLETE</span>'
            '<h2>Your Resume Analysis</h2>'
            '<p>Here is how your CV compares with the job requirements.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        overall = max(0, min(100, float(result["overall"])))

        st.markdown(
            f"""
            <div class="result-hero">
                <div class="ring" style="--p:{overall}">
                    <span>{html.escape(str(result["overall"]))}</span>
                </div>
                <div class="result-copy">
                    <span class="result-label">YOUR MATCH RESULT</span>
                    <h2>{html.escape(str(result["verdict"]))}</h2>
                    <p>
                        Based on skill coverage, semantic similarity,
                        and CV quality.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="metrics">'
            + metric("Skill Coverage", result["skill_score"])
            + metric("Meaning Match", result["semantic_score"])
            + metric("CV Quality", result["quality_score"])
            + "</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="medium")

        with c1:
            st.markdown(
                '<div class="section-title">✓ Skills You Have</div>'
                + chips(result["matched"], "good"),
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                '<div class="section-title">＋ Skills to Improve</div>'
                + chips(result["missing"], "bad"),
                unsafe_allow_html=True,
            )

        if result.get("extra"):
            st.markdown(
                '<div class="section-title">Other Skills on Your CV</div>'
                + chips(result["extra"], "neutral"),
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">✦ Personalized Suggestions</div>',
            unsafe_allow_html=True,
        )

        suggestions = result.get("suggestions", [])

        if suggestions:
            st.markdown(
                "".join(
                    f'<div class="tip">{html.escape(str(item))}</div>'
                    for item in suggestions
                ),
                unsafe_allow_html=True,
            )
        else:
            st.info("No additional suggestions available.")

        st.markdown(
            '<div class="section-title">CV Quality Checklist</div>',
            unsafe_allow_html=True,
        )

        for check in result.get("checks", []):
            status_class = "ok" if check["ok"] else "no"
            symbol = "✓" if check["ok"] else "!"
            st.markdown(
                f'<div class="check">'
                f'<span class="dot {status_class}">{symbol}</span>'
                f'{html.escape(str(check["label"]))}'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.download_button(
            "↓  Download Analysis Report",
            data=build_report(result),
            file_name="cv_analysis.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown(
        """
        <div class="feature-strip">
            <div><span>◎</span> Get Match Score</div>
            <div><span>✳</span> Identify Missing Skills</div>
            <div><span>♧</span> Personalized Suggestions</div>
            <div><span>◇</span> Improve Your CV</div>
        </div>
        <div class="footer-note">
            AI Resume Analyzer · Built to help you prepare for better opportunities.
        </div>
        """,
        unsafe_allow_html=True,
    )


# Sidebar navigation
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">▤</div>
            <div>
                <h2>AI Resume Analyzer</h2>
                <p>Smart Matching, Better Opportunities</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        ["Home", "About", "How It Works", "Settings"],
        label_visibility="collapsed",
        key="navigation",
    )

    st.markdown(
        """
        <div class="sidebar-quote">
            <span>“</span>
            <p>Your skills deserve<br>the right opportunity.</p>
            <div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if page == "Home":
    show_home()

elif page == "About":
    st.markdown(
        """
        <div class="page-heading">
            <span class="hero-badge">ABOUT THE PROJECT</span>
            <h1>AI Resume Analyzer</h1>
            <p>A tool to compare your CV with job requirements.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        This project analyzes resume content and compares it with a
        job description to highlight matching skills, missing skills,
        and possible improvements.

        **Important:** The match score is an estimate, not a hiring
        decision or a guarantee of job eligibility.
        """
    )

elif page == "How It Works":
    st.markdown(
        """
        <div class="page-heading">
            <span class="hero-badge">HOW IT WORKS</span>
            <h1>Three simple steps</h1>
            <p>Understand how to use the resume analyzer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        1. **Upload your CV:** Select a PDF, DOCX or TXT file.
        2. **Add a job description:** Paste the responsibilities and required skills.
        3. **Review your report:** Explore the match score, missing skills,
           suggestions and CV checklist.
        """
    )

else:
    st.markdown(
        """
        <div class="page-heading">
            <span class="hero-badge">PREFERENCES</span>
            <h1>Settings</h1>
            <p>Basic information about this application.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Supported resume formats: PDF, DOCX and TXT. "
        "Maximum upload size depends on your Streamlit configuration."
    )
    if st.button("Clear analysis results"):
        st.session_state.pop("result", None)
        st.session_state.pop("analysis_complete", None)
        st.rerun()
