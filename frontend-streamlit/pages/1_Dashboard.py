import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import get_request, post_request

# Page Config
st.set_page_config(page_title="Twin Dashboard", page_icon="📊", layout="wide")

# CSS Styling Injector
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Outfit', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(9, 14, 28, 1) 0%, rgba(17, 24, 39, 1) 90%);
        color: #F8FAFC;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    
    .grad-text {
        background: linear-gradient(135deg, #60A5FA 0%, #C084FC 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .score-badge {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin: 10px 0;
        line-height: 1;
    }
    
    .sub-badge {
        text-align: center;
        font-size: 1rem;
        color: #94A3B8;
        font-weight: 500;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication Guard
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔒 Please Login first in the Home page.")
    st.stop()

st.markdown("<h1>Placement Readiness <span class='grad-text'>Dashboard</span></h1>", unsafe_allow_html=True)

# Fetch stats from backend API
res = get_request("/api/dashboard/stats")
if not res or res.status_code != 200:
    st.info("💡 Set up your profile in the Home tab and upload your resume to see your placement calculations.")
    st.stop()
    
data = res.json()

# User onboarding guard
if not data.get("profile_exists", False):
    st.markdown("""
    <div class='glass-card' style='text-align: center; padding: 50px 30px; margin-top: 20px;'>
        <h2 style='color: #60A5FA; margin-top:0px;'>👋 Welcome to Placement Twin AI!</h2>
        <p style='color: #CBD5E1; font-size: 1.15rem; margin-top: 15px;'>
            Your digital career twin model has not been initialized yet.
        </p>
        <p style='color: #94A3B8; max-width: 600px; margin: 10px auto; line-height:1.6;'>
            To trigger agentic evaluation and construct your digital twin, go to the <b>Home</b> page in the sidebar, fill in your skills, career goals, and target companies, then click "Save & Update Twin Model".
        </p>
        <p style='color: #60A5FA; font-weight:600; margin-top: 20px;'>
            ⚙️ Once saved, our agent pipelines will execute and populate this dashboard instantly.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Layout
col1, col2 = st.columns([1, 1.8])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Twin Readiness Score")
    overall = data["readiness"]["overall_score"]
    
    # Render Score Badge with clean custom color
    if overall >= 80:
        color = "#10B981"  # Emerald Green
        verdict = "✓ Ready for Placements"
    elif overall >= 60:
        color = "#F59E0B"  # Amber Yellow
        verdict = "⏳ Needs Final Prep"
    else:
        color = "#EF4444"  # Coral Red
        verdict = "⚠️ High Skill Gap"
        
    st.markdown(f"<div class='score-badge' style='color: {color};'>{overall}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-badge'>{verdict}</div>", unsafe_allow_html=True)
    st.markdown(f"**Mentor's Assessment:**\n{data['readiness']['reasoning']}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Skill Radar
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("Balance Analysis")
    
    scores = data["readiness"]
    radar_df = pd.DataFrame(dict(
        r=[scores["resume_score"], scores["dsa_score"], scores["interview_score"], scores["skill_score"], scores["project_score"]],
        theta=["Resume", "DSA", "Interview", "Skill Match", "Project"]
    ))
    
    fig = px.line_polar(radar_df, r="r", theta="theta", line_close=True)
    fig.update_traces(fill="toself", line_color="#8B5CF6", fillcolor="rgba(139, 92, 246, 0.2)", line_width=2.5)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#94A3B8")),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#94A3B8")),
            bgcolor="rgba(0,0,0,0)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=25, t=30, b=25),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Daily task checklist
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🗓️ Today's Action Plan")
    
    tasks = data.get("daily_tasks", [])
    if not tasks:
        st.write("You don't have tasks generated for today. Save your profile details to trigger the daily planner agent.")
    else:
        for idx, task in enumerate(tasks):
            task_id = task.get("id", idx)
            if task_id is None:
                task_id = idx
            checked = st.checkbox(
                f"**{task.get('category')}**: {task.get('text')}", 
                value=task.get("completed", False),
                key=f"task_{task_id}_{idx}"
            )
            
            # If state changed, trigger sync update
            if checked != task.get("completed", False):
                post_request(f"/api/planner/tasks/{task_id}/toggle")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Motivation & Reminders panel
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("💡 Mentor Remarks & Motivation")
    
    mot_res = get_request("/api/planner/motivation")
    if mot_res and mot_res.status_code == 200:
        mot_data = mot_res.json()
        st.markdown(f"<blockquote style='font-style: italic; border-left: 4px solid #8B5CF6; padding-left: 10px; color: #CBD5E1;'>\"{mot_data.get('quote', 'Consistency is the engine of progress.')}\"</blockquote>", unsafe_allow_html=True)
        st.write("**Reminders Checklist:**")
        for idx, reminder in enumerate(mot_data.get("reminders", [])):
            st.write(f"• {reminder}")
    else:
        st.write("Configuring agent remark modules...")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Analytics Metrics
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📈 Consistency Metrics")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(
            label="DSA Questions Solved", 
            value=f"{data['dsa_stats']['solved']} / {data['dsa_stats']['total']}", 
            delta=f"{data['dsa_stats']['percentage']}% Done"
        )
    with col_b:
        st.metric(
            label="Mock Interviews Done", 
            value=f"{data['interview_stats']['count']}", 
            delta=f"Avg Score: {data['interview_stats']['average_score']}%"
        )
    with col_c:
        # Consistency score based on completed tasks
        completed_tasks = sum(1 for t in tasks if t.get("completed", False))
        total_tasks = len(tasks)
        consistency = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        st.metric(
            label="Daily Prep Consistency", 
            value=f"{consistency}%", 
            delta="Tasks Completed"
        )
    st.markdown("</div>", unsafe_allow_html=True)
