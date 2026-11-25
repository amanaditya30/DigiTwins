import os
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from app.core.config import settings

logger = logging.getLogger(__name__)

# Attempt to import langchain LLMs
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    try:
        from langchain_community.chat_models import ChatGroq
    except ImportError:
        ChatGroq = None


class MockLLM(BaseChatModel):
    """A simulated LLM chat model for offline testing and keyless execution."""
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        last_message = messages[-1].content.lower() if messages else ""
        
        # Default response payload
        response_text = "I am ready to help you with your placement goals."
        
        # Match prompt keywords to yield specific mock JSON outputs
        if "profile analysis" in last_message or "digital twin" in last_message:
            response_text = json.dumps({
                "strengths": ["Strong core programming knowledge", "Good understanding of fundamentals", "Good communication skills"],
                "weaknesses": ["Lacks project deployment experience", "Needs practice with hard DSA questions", "No certifications in target domain"],
                "focus_areas": ["Web Development", "DSA Problem Solving", "Cloud Deployment"]
            })
        elif "ats" in last_message or "resume" in last_message:
            response_text = json.dumps({
                "ats_score": 78,
                "strengths": ["Clear structure", "Action verbs used effectively", "Good skills list"],
                "improvements": ["Quantify impact in project achievements", "Add target keywords for software engineer roles", "Improve profile summary section"]
            })
        elif "skill gap" in last_message or "missing skills" in last_message:
            response_text = json.dumps({
                "matching_skills": ["Python", "JavaScript", "HTML/CSS", "SQL"],
                "missing_skills": ["React.js", "Docker", "FastAPI", "System Design Basics"],
                "relevance_percentage": 65
            })
        elif "roadmap" in last_message:
            response_text = json.dumps({
                "weekly_tasks": {
                    "Week 1": ["Revise Array sliding window problems", "Build a small FastAPI backend", "Update resume profile summary"],
                    "Week 2": ["Revise Linked List & Stack DSA problems", "Integrate Postgres with FastAPI", "Optimize resume project metrics"],
                    "Week 3": ["Revise Binary Search problems", "Learn Docker basics and containerize backend", "Complete 1 Mock Technical Interview"],
                    "Week 4": ["Revise Graph BFS/DFS", "Deploy application and build Streamlit dashboard", "Complete 1 Mock HR Interview"]
                },
                "monthly_tasks": {
                    "Month 1": ["Master Intermediate DSA and backend framework fundamentals", "Build 1 portfolio-grade full-stack project"],
                    "Month 2": ["Deep dive into System Design, databases, and complete mock interview rounds"]
                }
            })
        elif "dsa" in last_message or "questions" in last_message:
            response_text = json.dumps({
                "recommended_questions": [
                    {"name": "Two Sum", "topic": "Arrays", "difficulty": "Easy", "platform": "LeetCode"},
                    {"name": "Container With Most Water", "topic": "Arrays", "difficulty": "Medium", "platform": "LeetCode"},
                    {"name": "Longest Substring Without Repeating Characters", "topic": "Sliding Window", "difficulty": "Medium", "platform": "LeetCode"},
                    {"name": "Number of Islands", "topic": "Graphs", "difficulty": "Medium", "platform": "LeetCode"}
                ]
            })
        elif "project evaluation" in last_message or "github" in last_message:
            response_text = json.dumps({
                "score": 80,
                "suggestions": [
                    "Add detailed README.md describing database schema and API endpoints",
                    "Add custom error handlers to backend requests",
                    "Include unit tests for endpoints"
                ],
                "interview_questions": [
                    "How do you handle API security in this project?",
                    "What database pooling strategy did you use and why?"
                ]
            })
        elif "compatibility" in last_message or "match student" in last_message:
            response_text = json.dumps({
                "compatibility_score": 82,
                "matching_skills": ["Python", "SQL", "JavaScript"],
                "missing_skills": ["React", "FastAPI"],
                "recommendations": [
                    "Learn FastAPI and rewrite mock API tests",
                    "Solve 5 Medium questions on Arrays/Strings"
                ]
            })
        elif "readiness" in last_message or "score" in last_message:
            response_text = json.dumps({
                "overall_score": 76,
                "resume_score": 78,
                "dsa_score": 70,
                "interview_score": 80,
                "skill_score": 75,
                "project_score": 80,
                "reasoning": "You have a solid resume and project background. Your DSA practice needs more consistency, especially for Medium-Hard graph and tree algorithms. Practicing mock interviews will boost confidence further."
            })
        elif "planner" in last_message or "daily tasks" in last_message:
            response_text = json.dumps({
                "tasks": [
                    {"text": "Solve Leetcode 'Two Sum' problem", "category": "DSA", "completed": False},
                    {"text": "Refactor profile summary in resume", "category": "Resume", "completed": False},
                    {"text": "Revise Deadlock conditions in OS Notes", "category": "CS Fundamentals", "completed": False},
                    {"text": "Create simple FastAPI endpoint for profile review", "category": "Projects", "completed": False}
                ]
            })
        elif "motivation" in last_message or "reminders" in last_message:
            response_text = json.dumps({
                "quote": "Consistency beats talent when talent doesn't work hard. Take one step every day, and your placement success is guaranteed!",
                "reminders": [
                    "Complete today's DSA question practice.",
                    "Review your mock interview feedback report.",
                    "Update your portfolio project readme."
                ]
            })

        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _llm_type(self) -> str:
        return "mock-chat-llm"


def get_llm() -> BaseChatModel:
    """Retrieve LLM client wrapper based on configuration. Falls back to MockLLM if no credentials present."""
    provider = settings.PRIMARY_LLM_PROVIDER
    
    if provider == "openai":
        if settings.OPENAI_API_KEY and ChatOpenAI is not None:
            try:
                return ChatOpenAI(
                    model=settings.OPENAI_MODEL_NAME,
                    temperature=0.2,
                    openai_api_key=settings.OPENAI_API_KEY
                )
            except Exception as e:
                logger.warning(f"Error initializing OpenAI client: {e}. Falling back to MockLLM.")
        else:
            logger.warning("OpenAI API key missing or ChatOpenAI unavailable. Falling back to MockLLM.")
            
    elif provider == "groq":
        if settings.GROQ_API_KEY and ChatGroq is not None:
            try:
                return ChatGroq(
                    model=settings.GROQ_MODEL_NAME,
                    temperature=0.2,
                    groq_api_key=settings.GROQ_API_KEY
                )
            except Exception as e:
                logger.warning(f"Error initializing Groq client: {e}. Falling back to MockLLM.")
        else:
            logger.warning("Groq API key missing or ChatGroq unavailable. Falling back to MockLLM.")
            
    # Default fallback
    logger.info("Initializing offline MockLLM agent service.")
    return MockLLM()
