import streamlit as st
from utils.api_client import get_request, post_request

# Page configuration
st.set_page_config(page_title="AI Mock Interview", page_icon="🎤", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

# Authentication Guard
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please Login first in the Home page.")
    st.stop()

# Initialize session states for interview session
if "in_interview" not in st.session_state:
    st.session_state["in_interview"] = False
if "interview_id" not in st.session_state:
    st.session_state["interview_id"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "interview_complete" not in st.session_state:
    st.session_state["interview_complete"] = False

st.markdown("<h1>Mock Interview <span class='grad-text'>Coach Portal</span></h1>", unsafe_allow_html=True)

# Left column: Active Chat or Start Panel. Right column: Completed History or Scorecard.
col1, col2 = st.columns([2, 1])

with col1:
    if not st.session_state["in_interview"]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Configure New Mock Session")
        
        job_role = st.selectbox(
            "Target Job Role", 
            ["Software Engineer", "AI Engineer", "ML Engineer", "Data Scientist", "Backend Developer", "Frontend Developer"]
        )
        interview_type = st.selectbox("Round Type", ["Technical", "HR"])
        
        if st.button("Start Interview"):
            payload = {
                "job_role": job_role,
                "interview_type": interview_type
            }
            res = post_request("/api/interview/start", payload)
            if res and res.status_code == 200:
                data = res.json()
                st.session_state["in_interview"] = True
                st.session_state["interview_id"] = data["interview_id"]
                st.session_state["chat_history"] = [{"role": "interviewer", "text": data["question"]}]
                st.session_state["interview_complete"] = False
                st.success("Interview session initialized! Speak with the recruiter.")
                st.rerun()
            else:
                st.error("Failed to start mock session.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Active Session Chat")
        
        # Display current chat history
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "interviewer":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["text"])
            else:
                with st.chat_message("user", avatar="👨‍🎓"):
                    st.write(msg["text"])
                    
        # Check if interview was completed
        if st.session_state["interview_complete"]:
            st.write("---")
            st.info("Interview questions completed! Submit for analysis.")
            if st.button("Finish & Evaluate"):
                with st.spinner("Analyzing answers..."):
                    res = post_request(f"/api/interview/{st.session_state['interview_id']}/finish")
                    if res and res.status_code == 200:
                        st.session_state["in_interview"] = False
                        st.session_state["interview_id"] = None
                        st.session_state["interview_complete"] = False
                        st.session_state["latest_report"] = res.json()
                        st.success("Detailed score calculated successfully!")
                        st.rerun()
                    else:
                        st.error("Error generating report.")
        else:
            # Answer input
            answer_input = st.chat_input("Type your response here...")
            if answer_input:
                # Log student answer locally
                st.session_state["chat_history"].append({"role": "student", "text": answer_input})
                
                # Post answer to API
                payload = {"answer": answer_input}
                res = post_request(f"/api/interview/{st.session_state['interview_id']}/answer", payload)
                
                if res and res.status_code == 200:
                    data = res.json()
                    # Log interviewer next question
                    st.session_state["chat_history"].append({"role": "interviewer", "text": data["next_question"]})
                    if data.get("is_complete", False) or "interview complete" in data["next_question"].lower():
                        st.session_state["interview_complete"] = True
                    st.rerun()
                else:
                    st.error("Failed to submit response.")
                    
        # Cancel button
        if st.button("Quit Mock Session", key="quit_btn"):
            st.session_state["in_interview"] = False
            st.session_state["interview_id"] = None
            st.session_state["chat_history"] = []
            st.session_state["interview_complete"] = False
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Display latest report card or past score cards
    if "latest_report" in st.session_state and st.session_state["latest_report"]:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📊 Latest Session Scorecard")
        report = st.session_state["latest_report"]
        
        st.markdown(f"**Score:** <span style='font-size: 2.2rem; font-weight: 800; color: #10B981;'>{report.get('score')}%</span>", unsafe_allow_html=True)
        st.write(f"**Target Role:** {report.get('job_role')} ({report.get('interview_type')})")
        
        st.write("**Strengths:**")
        for s in report.get("feedback", {}).get("strengths", []):
            st.write(f"✅ {s}")
            
        st.write("**Weaknesses:**")
        for w in report.get("feedback", {}).get("weaknesses", []):
            st.write(f"⚠️ {w}")
            
        st.write("**Next Improvements:**")
        for sug in report.get("feedback", {}).get("suggestions", []):
            st.write(f"🚀 {sug}")
            
        if st.button("Close Report Card"):
            st.session_state["latest_report"] = None
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📚 Mock Interview History")
        
        hist_res = get_request("/api/interview")
        if hist_res and hist_res.status_code == 200:
            history = hist_res.json()
            if not history:
                st.write("No interviews logged yet.")
            else:
                for idx, item in enumerate(history):
                    # Format date
                    dt = item["created_at"][:10]
                    st.write(f"**{idx+1}. {item['job_role']} ({item['interview_type']})**")
                    st.write(f"Score: `{item['score']}%` | Date: `{dt}`")
                    st.write("---")
        st.markdown("</div>", unsafe_allow_html=True)
