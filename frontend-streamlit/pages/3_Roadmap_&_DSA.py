import streamlit as st
from utils.api_client import get_request, post_request

# Page configuration
st.set_page_config(page_title="Roadmap & DSA Advisor", page_icon="🗺️", layout="wide")

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
    .task-bullet {
        margin: 8px 0;
        padding-left: 10px;
        border-left: 3px solid #60A5FA;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Guard
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please Login first in the Home page.")
    st.stop()

st.markdown("<h1>Learning Roadmap & <span class='grad-text'>DSA Advisor</span></h1>", unsafe_allow_html=True)

# Fetch Roadmap details
roadmap_res = get_request("/api/roadmap")
if not roadmap_res or roadmap_res.status_code != 200:
    st.info("💡 Generate your profile to calculate learning roadmaps.")
    st.stop()
    
roadmap_data = roadmap_res.json()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🗺️ Weekly Learning Roadmap")
    
    weekly = roadmap_data.get("weekly_tasks", {})
    if not weekly:
        # Default mock roadmap if not yet calculated
        weekly = {
            "Week 1": ["Study Arrays & Two-pointer logic", "Audit your Resume formatting"],
            "Week 2": ["Study Stack, Queues, and Sliding window", "Learn FastAPI router setups"],
            "Week 3": ["Study Binary Search & basic Tree layouts", "Integrate SQLModel database storage"],
            "Week 4": ["Study Graph DFS/BFS algorithms", "Complete 1 full-turn Mock HR interview"]
        }
        
    for week, tasks in weekly.items():
        st.write(f"### {week}")
        for task in tasks:
            st.markdown(f"<div class='task-bullet'>{task}</div>", unsafe_allow_html=True)
            
    st.write("### 📅 Monthly High-Level Roadmap")
    monthly = roadmap_data.get("monthly_tasks", {})
    if not monthly:
        monthly = {
            "Month 1": ["Master intermediate coding structures and design a core API service"],
            "Month 2": ["Focus on System Design, SQL performance optimization, and mock technical assessments"]
        }
    for month, goals in monthly.items():
        st.write(f"**{month}:** {', '.join(goals)}")
        
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # DSA recommended questions
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🎯 Mentor Recommended DSA Questions")
    
    # We display a curated list matching the student's needs
    recs = [
        {"name": "Two Sum", "topic": "Arrays", "difficulty": "Easy", "platform": "LeetCode"},
        {"name": "Valid Parentheses", "topic": "Stacks", "difficulty": "Easy", "platform": "LeetCode"},
        {"name": "Longest Substring Without Repeating Characters", "topic": "Sliding Window", "difficulty": "Medium", "platform": "LeetCode"},
        {"name": "Number of Islands", "topic": "Graphs", "difficulty": "Medium", "platform": "LeetCode"}
    ]
    
    for idx, r in enumerate(recs):
        st.markdown(f"{idx+1}. **{r['name']}** ({r['topic']}) - `{r['difficulty']}` on *{r['platform']}*")
    st.markdown("</div>", unsafe_allow_html=True)

    # DSA progress Logger Form
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📥 Log DSA Progress")
    
    with st.form("dsa_logger_form"):
        topic = st.text_input("DSA Topic", value="Arrays")
        q_name = st.text_input("Question Name", value="Two Sum")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        status = st.selectbox("Status", ["Solved", "In Progress"])
        
        submitted = st.form_submit_button("Update Progress")
        if submitted:
            if topic and q_name:
                payload = {
                    "topic": topic,
                    "question_name": q_name,
                    "difficulty": difficulty,
                    "status": status
                }
                res = post_request("/api/roadmap/dsa/progress", payload)
                if res and res.status_code == 200:
                    st.success(f"Successfully logged: '{q_name}'!")
                    st.rerun()
                else:
                    st.error("Failed to update progress.")
            else:
                st.warning("Please fill question details.")
                
    st.markdown("</div>", unsafe_allow_html=True)

    # DSA history list
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📋 Your Solved Questions History")
    
    hist_res = get_request("/api/roadmap/dsa/progress")
    if hist_res and hist_res.status_code == 200:
        history = hist_res.json()
        if not history:
            st.write("No questions solved yet. Start practicing and logging questions!")
        else:
            for item in history:
                badge = "✅ Solved" if item["status"].lower() == "solved" else "⏳ Active"
                color = "#10B981" if item["status"].lower() == "solved" else "#F59E0B"
                st.markdown(
                    f"- **{item['question_name']}** ({item['topic']}) | "
                    f"`{item['difficulty']}` | "
                    f"<span style='color: {color}; font-weight: 600;'>{badge}</span>",
                    unsafe_allow_html=True
                )
    st.markdown("</div>", unsafe_allow_html=True)
