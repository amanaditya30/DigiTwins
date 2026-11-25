import streamlit as st
from utils.api_client import get_request, post_request

# Config
st.set_page_config(page_title="ATS Resume Auditor", page_icon="📝", layout="wide")

# CSS Styling Injector
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    * { font-family: 'Outfit', sans-serif; }
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(12, 19, 36, 1) 0%, rgba(21, 28, 48, 1) 90.1%);
        color: #F8FAFC;
    }
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    .grad-text {
        background: linear-gradient(to right, #60A5FA, #A78BFA, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .metric-val {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Guard
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please Login first in the Home page.")
    st.stop()

st.markdown("<h1>Resume Auditor & <span class='grad-text'>GenAI Copilot</span></h1>", unsafe_allow_html=True)

# Fetch stats (which contains resume scores)
stats_res = get_request("/api/dashboard/stats")
if not stats_res or stats_res.status_code != 200:
    st.info("💡 Set up your profile on the Home tab to configure your mentor.")
    st.stop()
    
stats_data = stats_res.json()

# Fetch detailed resume analysis from profile directly if needed, or rely on readiness scores
score_info = stats_data.get("readiness", {})
resume_score = score_info.get("resume_score", 0)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("ATS Review Report")
    
    if resume_score == 0:
        st.write("❌ No active resume audit found. Please upload your resume PDF on the Home page.")
    else:
        if resume_score >= 80:
            color = "#10B981"
            verdict = "Excellent Formatting & Relevance"
        elif resume_score >= 65:
            color = "#F59E0B"
            verdict = "Good start, needs refinement"
        else:
            color = "#EF4444"
            verdict = "Critically requires modifications"
            
        st.markdown(f"<div class='metric-val' style='color: {color};'>{resume_score}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-weight: 600; color: #94A3B8;'>{verdict}</p>", unsafe_allow_html=True)
        
        # In mock mode, agents yield these keys.
        # We can query profile directly for agent logs or display default suggestions.
        st.markdown("---")
        st.write("### 🔍 Bullet Suggestions")
        st.write("- **Strengths:** Strong formatting hierarchy, clean section layouts, and targeted technical skills declaration.")
        st.write("- **Improvements Required:** Quantify development impact metrics (e.g. rewrite 'responsible for frontend' to 'Improved frontend loading speed by 25% using virtual lists').")
        st.write("- **Missing Keywords:** System Design, Unit Testing, API Integration, Containerization.")
        
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛠️ GenAI Copilot Generators")
    
    tabs = st.tabs(["Cover Letter", "LinkedIn Post", "Optimize Bullet"])
    
    with tabs[0]:
        st.write("Draft a tailored cover letter for your target role.")
        job_role = st.text_input("Target Job Role", value=stats_data.get("career_goals", "Software Engineer"))
        target_company = st.text_input("Target Company Name", value="Google")
        
        if st.button("Generate Cover Letter"):
            with st.spinner("Drafting cover letter..."):
                payload = {
                    "type": "cover_letter",
                    "role": job_role,
                    "company": target_company
                }
                res = post_request("/api/profile/generate", payload)
                if res and res.status_code == 200:
                    st.text_area("Cover Letter Output", value=res.json()["content"], height=300)
                else:
                    st.error("Generation failed. Double-check your API key connection.")
                    
    with tabs[1]:
        st.write("Write an engaging LinkedIn post to announce milestones or skill acquisition.")
        topic = st.text_input("Topic / Milestone", value="FastAPI multi-agent frameworks")
        
        if st.button("Generate Post"):
            with st.spinner("Drafting LinkedIn Post..."):
                payload = {
                    "type": "linkedin_post",
                    "topic": topic
                }
                res = post_request("/api/profile/generate", payload)
                if res and res.status_code == 200:
                    st.text_area("LinkedIn Post Output", value=res.json()["content"], height=250)
                else:
                    st.error("Failed to generate post.")
                    
    with tabs[2]:
        st.write("Optimize a raw resume bullet point into an impact-oriented sentence.")
        raw_bullet = st.text_area("Raw Bullet Point", value="I worked on the frontend dashboard and added charts.")
        
        if st.button("Rewrite Bullet"):
            with st.spinner("Optimizing bullet phrasing..."):
                payload = {
                    "type": "resume_bullet",
                    "bullet": raw_bullet
                }
                res = post_request("/api/profile/generate", payload)
                if res and res.status_code == 200:
                    st.text_area("Optimized Bullet Output", value=res.json()["content"], height=150)
                else:
                    st.error("Failed to rewrite bullet.")
                    
    st.markdown("</div>", unsafe_allow_html=True)
