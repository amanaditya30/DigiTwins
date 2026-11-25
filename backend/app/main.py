import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.core.database import init_db, get_session
from app.api.api import api_router
from app.api.endpoints.auth import get_current_user
from app.models.domain import User, Profile, ReadinessScore, DSAProgress, MockInterview, DailyPlan
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Placement Twin AI API",
    description="Backend services for Multi-Agent Placement Twin Career Mentor.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Streamlit runs locally on a different port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup hook to initialize db
@app.on_event("startup")
def on_startup():
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database initialization complete.")


# Include sub-routers
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "app": "Placement Twin AI API",
        "status": "Running",
        "docs": "/docs"
    }


@app.get("/api/dashboard/stats")
def get_dashboard_stats(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Aggregates all placement readiness metrics, DSA logs, project scores, and mock interview analytics in a single call."""
    
    # 1. Fetch Profile
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    
    # 2. Fetch Readiness Score
    readiness = session.exec(select(ReadinessScore).where(ReadinessScore.user_id == current_user.id)).first()
    if not readiness:
        # Default scores if pipeline has not executed yet
        readiness = ReadinessScore(
            user_id=current_user.id,
            overall_score=0,
            resume_score=0,
            dsa_score=0,
            interview_score=0,
            skill_score=0,
            project_score=0,
            reasoning="Set up your profile and upload your resume to generate your placement readiness scorecard."
        )
        
    # 3. Fetch DSA counts
    dsa_logs = session.exec(select(DSAProgress).where(DSAProgress.user_id == current_user.id)).all()
    dsa_solved = sum(1 for q in dsa_logs if q.status.lower() == "solved")
    dsa_total = len(dsa_logs)
    
    # 4. Fetch Mock Interview history
    interviews = session.exec(select(MockInterview).where(MockInterview.user_id == current_user.id)).all()
    interview_scores = [i.score for i in interviews if i.score > 0]
    avg_interview_score = int(sum(interview_scores) / len(interview_scores)) if interview_scores else 0
    
    # 5. Fetch Daily Plan
    today = date.today()
    daily_plan = session.exec(
        select(DailyPlan).where(
            (DailyPlan.user_id == current_user.id) & (DailyPlan.plan_date == today)
        )
    ).first()
    
    daily_tasks = daily_plan.tasks if daily_plan else []
    
    # 6. Build response payload
    return {
        "readiness": {
            "overall_score": readiness.overall_score,
            "resume_score": readiness.resume_score,
            "dsa_score": readiness.dsa_score,
            "interview_score": readiness.interview_score,
            "skill_score": readiness.skill_score,
            "project_score": readiness.project_score,
            "reasoning": readiness.reasoning
        },
        "dsa_stats": {
            "solved": dsa_solved,
            "total": dsa_total,
            "percentage": int((dsa_solved / dsa_total) * 100) if dsa_total > 0 else 0
        },
        "interview_stats": {
            "count": len(interviews),
            "average_score": avg_interview_score,
            "scores": [i.score for i in interviews]
        },
        "daily_tasks": daily_tasks,
        "profile_exists": profile is not None,
        "skills": profile.skills if profile else [],
        "target_companies": profile.target_companies if profile else [],
        "career_goals": profile.career_goals if profile else ""
    }
