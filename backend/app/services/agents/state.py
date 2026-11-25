from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """The state schema shared across all nodes in the LangGraph multi-agent system."""
    user_id: int
    profile: Dict[str, Any]
    job_description: Optional[str]
    
    # Analysis & evaluations (populated by various agent nodes)
    profile_analysis: Dict[str, Any]
    resume_analysis: Dict[str, Any]
    skill_gap: Dict[str, Any]
    projects_analysis: List[Dict[str, Any]]
    
    # Plans & roadmaps
    learning_roadmap: Dict[str, Any]
    dsa_recommendations: Dict[str, Any]
    
    # Consolidated scoring and plans
    readiness_score: Dict[str, Any]
    daily_plan: Dict[str, Any]
    motivation: Dict[str, Any]
    
    errors: List[str]
