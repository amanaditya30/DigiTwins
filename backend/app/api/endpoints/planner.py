from datetime import date
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.api.endpoints.auth import get_current_user
from app.models.domain import User, DailyPlan, Profile, ReadinessScore
from app.services.agents.nodes.agent_nodes import daily_planner_node, motivation_node

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
def get_daily_plan(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Fetch today's planning schedule, generating one if not already created."""
    today = date.today()
    plan = session.exec(
        select(DailyPlan).where(
            (DailyPlan.user_id == current_user.id) & (DailyPlan.plan_date == today)
        )
    ).first()
    
    if plan:
        return {
            "id": plan.id,
            "plan_date": plan.plan_date,
            "tasks": plan.tasks
        }
        
    # Generate new daily plan using the Agent node
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    if not profile:
        # Default plan if profile doesn't exist yet
        default_tasks = [
            {"id": 0, "text": "Set up your Profile details in the Dashboard", "category": "Profile", "completed": False},
            {"id": 1, "text": "Upload your resume for ATS review", "category": "Resume", "completed": False},
            {"id": 2, "text": "Solve 1 Array topic questions", "category": "DSA", "completed": False},
            {"id": 3, "text": "Start a mock Technical interview", "category": "Interview", "completed": False}
        ]
        new_plan = DailyPlan(
            user_id=current_user.id,
            plan_date=today,
            tasks=default_tasks
        )
        session.add(new_plan)
        session.commit()
        session.refresh(new_plan)
        return {
            "id": new_plan.id,
            "plan_date": new_plan.plan_date,
            "tasks": new_plan.tasks
        }
        
    # Generate via agent
    mock_state = {
        "user_id": current_user.id,
        "profile": {
            "career_goals": profile.career_goals,
            "skills": profile.skills
        },
        "learning_roadmap": {},
        "dsa_recommendations": {}
    }
    
    node_result = daily_planner_node(mock_state)
    tasks_data = node_result.get("daily_plan", {}).get("tasks", [])
    
    # Assign integer IDs to tasks
    formatted_tasks = []
    for idx, task in enumerate(tasks_data):
        formatted_tasks.append({
            "id": idx,
            "text": task.get("text", "Practice coding task"),
            "category": task.get("category", "General"),
            "completed": task.get("completed", False)
        })
        
    new_plan = DailyPlan(
        user_id=current_user.id,
        plan_date=today,
        tasks=formatted_tasks
    )
    
    session.add(new_plan)
    session.commit()
    session.refresh(new_plan)
    
    return {
        "id": new_plan.id,
        "plan_date": new_plan.plan_date,
        "tasks": new_plan.tasks
    }


@router.post("/tasks/{task_id}/toggle")
def toggle_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle completion status of a planner task."""
    today = date.today()
    plan = session.exec(
        select(DailyPlan).where(
            (DailyPlan.user_id == current_user.id) & (DailyPlan.plan_date == today)
        )
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found for today.")
        
    updated_tasks = []
    task_found = False
    
    for task in plan.tasks:
        if task.get("id") == task_id:
            task["completed"] = not task.get("completed", False)
            task_found = True
        updated_tasks.append(task)
        
    if not task_found:
        raise HTTPException(status_code=404, detail="Task ID not found in plan.")
        
    # Overwrite JSON attribute
    plan.tasks = updated_tasks
    session.add(plan)
    session.commit()
    
    return {"message": "Task status updated successfully", "tasks": plan.tasks}


@router.get("/motivation")
def get_motivation(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Retrieve daily motivation quotes and checkmarks using the Motivation Agent."""
    readiness = session.exec(select(ReadinessScore).where(ReadinessScore.user_id == current_user.id)).first()
    score = readiness.overall_score if readiness else 70
    
    mock_state = {
        "readiness_score": {"overall_score": score}
    }
    
    result = motivation_node(mock_state)
    return result.get("motivation", {})
