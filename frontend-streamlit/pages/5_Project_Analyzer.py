import streamlit as st
from utils.api_client import get_request, post_request

# Config
st.set_page_config(page_title="Project Auditor", page_icon="💻", layout="wide")

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
    .proj-score {
        font-size: 2.5rem;
        font-weight: 800;
        color: #10B981;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Guard
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please Login first in the Home page.")
    st.stop()

st.markdown("<h1>Project Evaluation & <span class='grad-text'>Auditor</span></h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Register & Audit Coding Project")
    
    with st.form("project_form"):
        title = st.text_input("Project Title", value="Task Manager App")
        desc = st.text_area("Project Description (Details, Stack, Architecture)", value="A web API for managing to-dos. Built using FastAPI, PostgreSQL, and Docker containerization. Implements OAuth2 security and connection pool strategies.")
        repo_url = st.text_input("GitHub / Repository URL (Optional)", value="https://github.com/user/task-manager")
        
        submitted = st.form_submit_button("Audit Project")
        if submitted:
            if title and desc:
                payload = {
                    "title": title,
                    "description": desc,
                    "repo_url": repo_url
                }
                with st.spinner("Analyzing project with Project Evaluation Agent..."):
                    res = post_request("/api/projects", payload)
                    if res and res.status_code == 200:
                        st.success(f"Audit completed for '{title}'!")
                        st.rerun()
                    else:
                        st.error("Failed to complete audit.")
            else:
                st.warning("Please fill project title and description.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📚 Audited Projects Portfolio")
    
    res = get_request("/api/projects")
    if res and res.status_code == 200:
        projects = res.json()
        if not projects:
            st.write("No audited projects yet. Fill the form to trigger audits.")
        else:
            for proj in projects:
                st.markdown(f"### {proj['title']}")
                if proj.get("repo_url"):
                    st.markdown(f"🔗 [Repository Link]({proj['repo_url']})")
                
                col_score, col_gen = st.columns([1, 1])
                with col_score:
                    st.markdown(f"<div class='proj-score'>Score: {proj['score']}%</div>", unsafe_allow_html=True)
                with col_gen:
                    if st.button("Generate Markdown README", key=f"readme_{proj['id']}"):
                        with st.spinner("Generating README documentation..."):
                            payload = {
                                "type": "project_doc",
                                "title": proj["title"],
                                "description": proj["description"]
                            }
                            gen_res = post_request("/api/profile/generate", payload)
                            if gen_res and gen_res.status_code == 200:
                                st.session_state[f"readme_text_{proj['id']}"] = gen_res.json()["content"]
                            else:
                                st.error("Failed to generate documentation.")
                                
                if f"readme_text_{proj['id']}" in st.session_state:
                    st.markdown("##### 📄 Generated README.md:")
                    st.code(st.session_state[f"readme_text_{proj['id']}"], language="markdown")
                    
                st.write("**Improvements Suggestions:**")
                for sug in proj.get("suggestions", []):
                    st.write(f"- {sug}")
                    
                st.write("**Recruiter Interview Questions:**")
                for q in proj.get("interview_questions", []):
                    st.write(f"❓ *{q}*")
                    
                st.write("---")
    else:
        st.write("Generating projects...")
    st.markdown("</div>", unsafe_allow_html=True)
