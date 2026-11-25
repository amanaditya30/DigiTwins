from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.api.endpoints.auth import get_current_user
from app.models.domain import User, Project
from app.models.schemas import ProjectCreate, ProjectResponse
from app.services.agents.nodes.agent_nodes import project_evaluator_node

router = APIRouter()

@router.get("", response_model=List[ProjectResponse])
def list_projects(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """List all analyzed projects for the student."""
    projects = session.exec(select(Project).where(Project.user_id == current_user.id)).all()
    return projects


@router.post("", response_model=ProjectResponse)
def evaluate_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Register a new project, invoke the Project Evaluation Agent, and save recommendations and mock questions."""
    # Execute the agent logic by simulating state
    mock_state = {
        "user_id": current_user.id,
        "profile": {
            "projects": [{"title": project_in.title, "description": project_in.description}],
            "academic_history": ""
        },
        "projects_analysis": []
    }
    
    # Call the node function
    node_result = project_evaluator_node(mock_state)
    analysis_list = node_result.get("projects_analysis", [])
    
    if not analysis_list:
        raise HTTPException(status_code=500, detail="Project Evaluation Agent failed to return results.")
        
    analysis = analysis_list[0]
    
    new_project = Project(
        user_id=current_user.id,
        title=project_in.title,
        description=project_in.description,
        repo_url=project_in.repo_url,
        score=analysis.get("score", 70),
        suggestions=analysis.get("suggestions", []),
        interview_questions=analysis.get("interview_questions", [])
    )
    
    session.add(new_project)
    session.commit()
    session.refresh(new_project)
    return new_project
