import pypdf
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlmodel import Session, select
from app.core.database import get_session
from app.api.endpoints.auth import get_current_user
from app.models.domain import User, Profile, ReadinessScore, Roadmap, DailyPlan
from app.models.schemas import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.agents.graph import run_placement_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

def sync_profile_with_agents(user_id: int, profile_db: Profile, session: Session):
    """Executes the LangGraph pipeline to update digital twin stats and persists results to database tables."""
    try:
        profile_data = {
            "full_name": profile_db.full_name,
            "skills": profile_db.skills,
            "interests": profile_db.interests,
            "target_companies": profile_db.target_companies,
            "career_goals": profile_db.career_goals,
            "academic_history": profile_db.academic_history,
            "resume_text": profile_db.resume_text
        }
        
        # Run LangGraph pipeline
        result_state = run_placement_pipeline(user_id=user_id, profile_data=profile_data)
        
        # Save Readiness Score
        score_data = result_state.get("readiness_score", {})
        if score_data:
            db_score = session.exec(select(ReadinessScore).where(ReadinessScore.user_id == user_id)).first()
            if not db_score:
                db_score = ReadinessScore(user_id=user_id)
            db_score.overall_score = score_data.get("overall_score", 0)
            db_score.resume_score = score_data.get("resume_score", 0)
            db_score.dsa_score = score_data.get("dsa_score", 0)
            db_score.interview_score = score_data.get("interview_score", 0)
            db_score.skill_score = score_data.get("skill_score", 0)
            db_score.project_score = score_data.get("project_score", 0)
            db_score.reasoning = score_data.get("reasoning", "")
            db_score.updated_at = datetime.utcnow()
            session.add(db_score)
            
        # Save Learning Roadmap
        roadmap_data = result_state.get("learning_roadmap", {})
        if roadmap_data:
            db_roadmap = session.exec(select(Roadmap).where(Roadmap.user_id == user_id)).first()
            if not db_roadmap:
                db_roadmap = Roadmap(user_id=user_id)
            db_roadmap.weekly_tasks = roadmap_data.get("weekly_tasks", {})
            db_roadmap.monthly_tasks = roadmap_data.get("monthly_tasks", {})
            db_roadmap.updated_at = datetime.utcnow()
            session.add(db_roadmap)
            
        # Save Daily Plan
        plan_data = result_state.get("daily_plan", {})
        if plan_data and "tasks" in plan_data:
            formatted_tasks = []
            for idx, task in enumerate(plan_data.get("tasks", [])):
                formatted_tasks.append({
                    "id": idx,
                    "text": task.get("text", "Practice coding task"),
                    "category": task.get("category", "General"),
                    "completed": task.get("completed", False)
                })
            db_plan = DailyPlan(
                user_id=user_id,
                tasks=formatted_tasks,
                completed_tasks=[]
            )
            session.add(db_plan)
            
        session.commit()
    except Exception as e:
        logger.error(f"Failed to synchronize profile stats via agents: {e}")
        session.rollback()


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Fetch current user's profile."""
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please create one.")
    return profile


@router.post("", response_model=ProfileResponse)
def create_or_update_profile(
    profile_in: ProfileCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Create or update profile details, initiating background pipeline synchronization."""
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=profile_in.full_name,
            skills=profile_in.skills,
            interests=profile_in.interests,
            target_companies=profile_in.target_companies,
            career_goals=profile_in.career_goals,
            academic_history=profile_in.academic_history,
            resume_text=profile_in.resume_text or ""
        )
    else:
        profile.full_name = profile_in.full_name
        profile.skills = profile_in.skills
        profile.interests = profile_in.interests
        profile.target_companies = profile_in.target_companies
        profile.career_goals = profile_in.career_goals
        profile.academic_history = profile_in.academic_history
        if profile_in.resume_text:
            profile.resume_text = profile_in.resume_text
            
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    
    # Run the Multi-Agent pipeline in the background to avoid blocking API response
    background_tasks.add_task(sync_profile_with_agents, current_user.id, profile, session)
    
    return profile


@router.post("/resume", response_model=ProfileResponse)
def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Uploads a PDF resume, parses its text contents, and triggers the placement twin agent pipeline."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")
        
    try:
        reader = pypdf.PdfReader(file.file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        logger.error(f"Failed to parse resume PDF: {e}")
        raise HTTPException(status_code=400, detail="Could not read PDF contents.")
        
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=current_user.username,
            skills=[],
            interests=[],
            target_companies=[],
            career_goals="",
            academic_history="",
            resume_text=text,
            resume_filename=file.filename
        )
    else:
        profile.resume_text = text
        profile.resume_filename = file.filename
        
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    
    # Trigger AI multi-agent graph re-run
    background_tasks.add_task(sync_profile_with_agents, current_user.id, profile, session)
    
    return profile


@router.post("/generate")
def generate_genai_asset(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Generates GenAI materials like custom Cover Letters, optimized Resume Bullets, LinkedIn posts, or Markdown READMEs."""
    asset_type = payload.get("type")
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Please set up your profile details first.")
        
    from app.services.agents.llm import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage
    
    llm = get_llm()
    
    if asset_type == "cover_letter":
        role = payload.get("role", "Software Engineer")
        company = payload.get("company", "Target Company")
        prompt = f"""
        Write a professional cover letter for a student applying for the role of {role} at {company}.
        Student Details:
        - Name: {profile.full_name}
        - Skills: {', '.join(profile.skills)}
        - Goals: {profile.career_goals}
        Keep the letter clear, compelling, and exactly formatted for a cover letter.
        """
    elif asset_type == "linkedin_post":
        topic = payload.get("topic", "Software Development")
        prompt = f"""
        Write an engaging LinkedIn post for a student talking about their learnings in {topic} or showcasing a new coding project.
        Include hashtags and professional tone.
        Student Details:
        - Name: {profile.full_name}
        - Skills: {', '.join(profile.skills)}
        """
    elif asset_type == "resume_bullet":
        bullet = payload.get("bullet", "")
        prompt = f"""
        Refactor the following resume bullet point to make it sound professional and quantified for an ATS system. Use action verbs and include metrics/impact examples where possible.
        Bullet: "{bullet}"
        """
    elif asset_type == "project_doc":
        title = payload.get("title", "My Project")
        desc = payload.get("description", "A coding project")
        prompt = f"""
        Write a professional, comprehensive markdown README documentation template for the project: "{title}".
        Description: "{desc}"
        Include: Features, Tech Stack, Architecture (represented as text), and How to Run.
        """
    else:
        raise HTTPException(status_code=400, detail="Invalid asset type requested.")
        
    try:
        messages = [
            SystemMessage(content="You are a senior tech writer, copywriter, and career strategist."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        return {"content": res.content}
    except Exception as e:
        logger.error(f"Error generating GenAI content: {e}")
        return {"content": f"Generation failed: {str(e)}. (Fallback template): Please ensure your API keys are configured."}


@router.post("/match")
def match_job_description(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Compares the student's digital twin profile against a job description and evaluates compatibility."""
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please create one.")
        
    from app.services.agents.nodes.agent_nodes import job_matching_node
    
    mock_state = {
        "profile": {
            "skills": profile.skills,
            "career_goals": profile.career_goals
        },
        "job_description": payload.get("job_description", "")
    }
    
    result = job_matching_node(mock_state)
    match_res = result.get("job_match", {})
    return match_res


