import streamlit as st
import json
from utils.api_client import login_user, register_user, get_request, post_request, post_file_request

# Page Configuration
st.set_page_config(
    page_title="Placement Twin AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sleek Premium Styling Injector
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek gradient background for main container */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(9, 14, 28, 1) 0%, rgba(17, 24, 39, 1) 90%);
        color: #F8FAFC;
    }
    
    /* Card Glassmorphism layout */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 20px;
        padding: 28px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin-bottom: 24px;
    }
    
    /* Form sections */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #60A5FA;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(96, 165, 250, 0.15);
        padding-bottom: 6px;
    }

    /* Primary Gradient Button hover elements */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 28px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.55);
        color: white;
    }
    
    /* Header custom styles */
    .grad-text {
        background: linear-gradient(135deg, #60A5FA 0%, #C084FC 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Sidebar spacing and background */
    .css-1d391tw {
        background-color: #0B0F19 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# Sidebar branding
st.sidebar.markdown("<h2 class='grad-text' style='text-align:center;'>Placement Twin</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align:center; color:#94A3B8; font-size:0.9rem;'>🤖 Autonomous AI Career Twin</p>", unsafe_allow_html=True)

if not st.session_state["authenticated"]:
    # Main Welcome Header
    col1, col2 = st.columns([1.4, 1])
    with col1:
        st.markdown("<h1 style='font-size: 3.8rem; line-height: 1.1; margin-bottom: 0px;'>Meet Your <br><span class='grad-text'>Placement Twin</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 1.25rem; font-weight: 400; margin-top: 15px; max-width: 550px;'>Build a digital replica of your skills, resume, and code repos to receive automated, agentic career guidance and mock assessments.</p>", unsafe_allow_html=True)
        st.markdown("""
        <div class='glass-card' style='margin-top: 35px;'>
            <h3 style='margin-top:0px; color:#F1F5F9;'>⚙️ Full-Stack Multi-Agent System</h3>
            <div style='margin-top:15px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                <div>
                    <h5 style='color:#60A5FA; margin-bottom:5px;'>🧠 LangGraph Engine</h5>
                    <p style='color:#94A3B8; font-size:0.9rem; margin-top:0px;'>Routes profile updates through a DAG of 9 specialized evaluation agents.</p>
                </div>
                <div>
                    <h5 style='color:#C084FC; margin-bottom:5px;'>🔍 ATS Resume Audit</h5>
                    <p style='color:#94A3B8; font-size:0.9rem; margin-top:0px;'>Generates metrics scores, extracts weaknesses, and optimizes job matching.</p>
                </div>
                <div>
                    <h5 style='color:#F472B6; margin-bottom:5px;'>🎤 Interactive Mocks</h5>
                    <p style='color:#94A3B8; font-size:0.9rem; margin-top:0px;'>Chat interface with turn-based technical & HR recruiter loops.</p>
                </div>
                <div>
                    <h5 style='color:#34D399; margin-bottom:5px;'>📚 RAG Notes Store</h5>
                    <p style='color:#94A3B8; font-size:0.9rem; margin-top:0px;'>Embeds study notes in ChromaDB to advice roadmaps and mocks.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card' style='margin-top: 20px;'>", unsafe_allow_html=True)
        auth_mode = st.radio("Join Placement Twin", ["Login", "Register"], label_visibility="collapsed")
        
        if auth_mode == "Login":
            st.markdown("<h3 style='margin-top:0px;'>Sign In</h3>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="e.g. johndoe")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            if st.button("Enter Dashboard"):
                if username and password:
                    res = login_user(username, password)
                    if res and res.status_code == 200:
                        data = res.json()
                        st.session_state["authenticated"] = True
                        st.session_state["token"] = data["access_token"]
                        st.session_state["username"] = username
                        st.success("Access Granted! Welcome.")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.warning("Fields cannot be empty.")
                    
        else:
            st.markdown("<h3 style='margin-top:0px;'>Create Account</h3>", unsafe_allow_html=True)
            new_user = st.text_input("Username", placeholder="Choose username")
            new_email = st.text_input("Email Address", placeholder="Enter email")
            new_pass = st.text_input("Password", type="password", placeholder="Choose secure password")
            if st.button("Create Account"):
                if new_user and new_email and new_pass:
                    res = register_user(new_user, new_email, new_pass)
                    if res and res.status_code == 201:
                        data = res.json()
                        st.session_state["authenticated"] = True
                        st.session_state["token"] = data["access_token"]
                        st.session_state["username"] = new_user
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to register. Username/Email might be taken.")
                else:
                    st.warning("Please fill all details.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Authenticated user dashboard Welcome & Configuration
    st.markdown(f"<h1>Digital Twin <span class='grad-text'>Control Panel</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:1.1rem; margin-top:-10px;'>Configure your professional profile details below. Specialized agents will evaluate your metrics and update your dashboard analytics.</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.06); margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Fetch active profile
    res = get_request("/api/profile")
    profile_exists = res is not None and res.status_code == 200
    
    profile_data = {}
    if profile_exists:
        profile_data = res.json()
        
    main_tabs = st.tabs(["👤 Profile Setup Details", "📄 Ingest Resume PDF"])
    
    with main_tabs[0]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Configure Professional Identity</div>", unsafe_allow_html=True)
        
        # Sub tabs for cleaner fields grouping
        sub_tabs = st.tabs(["Personal & Goals", "Skills & Interests", "Academics"])
        
        with sub_tabs[0]:
            col_name, col_goals = st.columns(2)
            with col_name:
                full_name = st.text_input("Full Name", value=profile_data.get("full_name", ""), placeholder="e.g. John Doe")
            with col_goals:
                career_goals = st.text_input("Career Goals / Job Role", value=profile_data.get("career_goals", "Software Engineer"), placeholder="e.g. Backend AI Developer")
            target_companies = st.text_input("Target Companies (comma-separated)", value=", ".join(profile_data.get("target_companies", [])), placeholder="e.g. Google, Amazon, Stripe")
            
        with sub_tabs[1]:
            skills = st.text_area("Core Skills (comma-separated)", value=", ".join(profile_data.get("skills", [])), placeholder="e.g. Python, SQL, Docker, React, FastAPI")
            interests = st.text_area("Tech Interests / Domains (comma-separated)", value=", ".join(profile_data.get("interests", [])), placeholder="e.g. Generative AI, RAG, Microservices")
            
        with sub_tabs[2]:
            academic_history = st.text_area("Academic History & Scores (Degree, GPA, Marks)", value=profile_data.get("academic_history", ""), placeholder="e.g. B.Tech in CS: 8.9 CGPA, High school: 92%")
            
        st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
        if st.button("Save & Update Twin Model"):
            if full_name and skills:
                skills_list = [s.strip() for s in skills.split(",") if s.strip()]
                interests_list = [i.strip() for i in interests.split(",") if i.strip()]
                target_list = [t.strip() for t in target_companies.split(",") if t.strip()]
                
                payload = {
                    "full_name": full_name,
                    "skills": skills_list,
                    "interests": interests_list,
                    "target_companies": target_list,
                    "career_goals": career_goals,
                    "academic_history": academic_history,
                    "resume_text": profile_data.get("resume_text", "")
                }
                
                with st.spinner("Invoking LangGraph Multi-Agent pipeline..."):
                    save_res = post_request("/api/profile", payload)
                    if save_res and save_res.status_code == 200:
                        st.success("Twin Profile updated! Dashboard metrics will reflect these updates in the sidebar tabs.")
                    else:
                        st.error("Failed to save profile.")
            else:
                st.warning("Please fill your Full Name and Skills.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with main_tabs[1]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Upload Active Resume</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose PDF Resume File", type="pdf")
        if uploaded_file is not None:
            if st.button("Extract & Sync Resume Details"):
                with st.spinner("Ingesting PDF, extracting keywords, and scoring layout..."):
                    res = post_file_request("/api/profile/resume", uploaded_file.getvalue(), uploaded_file.name)
                    if res and res.status_code == 200:
                        st.success("Resume parsed successfully! Agent score calculations updated.")
                        st.rerun()
                    else:
                        st.error("Error processing resume PDF.")
                        
        if profile_exists and profile_data.get("resume_filename"):
            st.success(f"✓ Currently active resume: **{profile_data.get('resume_filename')}**")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Logout action
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out"):
        st.session_state["authenticated"] = False
        st.session_state["token"] = None
        st.session_state["username"] = None
        st.rerun()
