import logging
from langgraph.graph import StateGraph, END
from app.services.agents.state import AgentState
from app.services.agents.nodes import (
    profile_analyzer_node,
    resume_evaluator_node,
    skill_gap_node,
    project_evaluator_node,
    roadmap_agent_node,
    dsa_agent_node,
    readiness_score_node,
    daily_planner_node,
    motivation_node,
    job_matching_node
)

logger = logging.getLogger(__name__)

def create_agent_graph():
    """Builds and compiles the multi-agent execution DAG."""
    workflow = StateGraph(AgentState)
    
    # Register agent nodes
    workflow.add_node("profile_analyzer", profile_analyzer_node)
    workflow.add_node("resume_evaluator", resume_evaluator_node)
    workflow.add_node("skill_gap", skill_gap_node)
    workflow.add_node("project_evaluator", project_evaluator_node)
    workflow.add_node("roadmap_gen", roadmap_agent_node)
    workflow.add_node("dsa_advisor", dsa_agent_node)
    workflow.add_node("readiness_score", readiness_score_node)
    workflow.add_node("daily_planner", daily_planner_node)
    workflow.add_node("motivation", motivation_node)
    workflow.add_node("job_matcher", job_matching_node)
    
    # Establish edges (DAG Flow)
    workflow.set_entry_point("profile_analyzer")
    
    workflow.add_edge("profile_analyzer", "resume_evaluator")
    workflow.add_edge("resume_evaluator", "skill_gap")
    workflow.add_edge("skill_gap", "project_evaluator")
    workflow.add_edge("project_evaluator", "roadmap_gen")
    workflow.add_edge("roadmap_gen", "dsa_advisor")
    workflow.add_edge("dsa_advisor", "readiness_score")
    workflow.add_edge("readiness_score", "daily_planner")
    workflow.add_edge("daily_planner", "motivation")
    
    # Conditionally route or complete graph
    workflow.add_edge("motivation", "job_matcher")
    workflow.add_edge("job_matcher", END)
    
    return workflow.compile()


# Compile graph singleton
placement_agent_graph = create_agent_graph()


def run_placement_pipeline(user_id: int, profile_data: dict, job_description: str = None) -> dict:
    """Executes the multi-agent graph with initial inputs and returns the final updated state."""
    logger.info(f"Triggering placement twin agent pipeline for user {user_id}")
    
    initial_state = AgentState(
        user_id=user_id,
        profile=profile_data,
        job_description=job_description,
        profile_analysis={},
        resume_analysis={},
        skill_gap={},
        projects_analysis=[],
        learning_roadmap={},
        dsa_recommendations={},
        readiness_score={},
        daily_plan={},
        motivation={},
        errors=[]
    )
    
    try:
        final_state = placement_agent_graph.invoke(initial_state)
        return final_state
    except Exception as e:
        logger.error(f"Error running placement agent graph: {e}")
        initial_state["errors"].append(f"Pipeline execution failed: {str(e)}")
        return initial_state
