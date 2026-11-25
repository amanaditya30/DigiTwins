import streamlit as st
from utils.api_client import get_request, post_request

# Config
st.set_page_config(page_title="Job Matcher", page_icon="🤝", layout="wide")

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
    .match-score {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Guard
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please Login first in the Home page.")
    st.stop()

st.markdown("<h1>Job Matching <span class='grad-text'>Auditor</span></h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Paste Job Description")
    st.write("Compare your digital twin's current profile details against a target job posting.")
    
    jd_input = st.text_area(
        "Job Description Text", 
        height=300,
        placeholder="We are looking for a Software Engineer with experience in Python, FastAPI, SQL, Docker, and REST APIs..."
    )
    
    run_match = st.button("Compare Compatibility")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if run_match and jd_input:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🔍 Matching Results")
        
        with st.spinner("Analyzing alignment..."):
            payload = {"job_description": jd_input}
            res = post_request("/api/profile/match", payload)
            
            if res and res.status_code == 200:
                data = res.json()
                score = data.get("compatibility_score", 0)
                
                if score >= 80:
                    color = "#10B981"
                elif score >= 60:
                    color = "#F59E0B"
                else:
                    color = "#EF4444"
                    
                st.markdown(f"<div class='match-score' style='color: {color};'>{score}% Match</div>", unsafe_allow_html=True)
                
                st.write("### ✅ Matching Skills")
                matching = data.get("matching_skills", [])
                if matching:
                    st.write(", ".join(matching))
                else:
                    st.write("*No skills matched. Double check your profile configurations.*")
                    
                st.write("### ⚠️ Missing Skills")
                missing = data.get("missing_skills", [])
                if missing:
                    st.write(", ".join(missing))
                else:
                    st.write("*None! You have all the skills requested.*")
                    
                st.write("### 🚀 Recruiter Recommendations")
                recs = data.get("recommendations", [])
                for idx, r in enumerate(recs):
                    st.write(f"{idx+1}. {r}")
            else:
                st.error("Failed to run match. Make sure backend is running.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.info("Paste a Job Description in the left box and click 'Compare Compatibility' to evaluate your alignment.")
        st.markdown("</div>", unsafe_allow_html=True)
