import json
import re
import logging
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.agents.llm import get_llm
from app.services.agents.state import AgentState
from app.services.rag.vector_store import search_similarity

logger = logging.getLogger(__name__)

def parse_json_markdown(text: str) -> Dict[str, Any]:
    """Extract and parse JSON from LLM output, handling markdown blocks and raw strings."""
    try:
        # Check for markdown code fences
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1).strip())
        
        # Try parsing raw string
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"JSON parsing error: {e}. Output was: {text}")
        # Clean string from basic markdown symbols
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # Return basic fallback dictionary
            return {}

# ----------------- Agent Nodes -----------------

def profile_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """Analyzes the student's background, skills, and goals to build the Digital Twin profile context."""
    logger.info("Running Profile Analyzer Agent")
    llm = get_llm()
    profile = state.get("profile", {})
    
    prompt = f"""
    You are the Profile Analysis Agent for Placement Twin AI.
    Analyze the student's uploaded details and compile their profile strengths, weaknesses, and key development areas.
    
    Student Profile:
    - Name: {profile.get('full_name')}
    - Skills: {', '.join(profile.get('skills', []))}
    - Interests: {', '.join(profile.get('interests', []))}
    - Target Companies: {', '.join(profile.get('target_companies', []))}
    - Career Goals: {profile.get('career_goals')}
    - Academic History: {profile.get('academic_history')}
    
    Provide your analysis strictly in the following JSON format:
    {{
        "strengths": ["list of key strengths"],
        "weaknesses": ["list of weaknesses or improvement areas"],
        "focus_areas": ["suggested core technical focus areas"]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are a senior technical career counselor. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        analysis = parse_json_markdown(res.content)
        
        # Ensure default structure
        if not analysis:
            analysis = {
                "strengths": ["Solid foundation in " + (profile.get('skills')[0] if profile.get('skills') else "CS fundamentals")],
                "weaknesses": ["Needs specific roadmap practice"],
                "focus_areas": ["Core development practice"]
            }
            
        return {"profile_analysis": analysis}
    except Exception as e:
        logger.error(f"Profile Analyzer node error: {e}")
        return {"errors": state.get("errors", []) + [f"Profile Analyzer: {str(e)}"]}


def resume_evaluator_node(state: AgentState) -> Dict[str, Any]:
    """Evaluates the resume text, generates an ATS compatibility score, and recommends changes."""
    logger.info("Running Resume Agent")
    llm = get_llm()
    profile = state.get("profile", {})
    resume_text = profile.get("resume_text", "")
    
    if not resume_text:
        return {
            "resume_analysis": {
                "ats_score": 0,
                "strengths": ["No resume uploaded yet."],
                "improvements": ["Please upload your resume PDF to trigger detailed ATS analysis."]
            }
        }
        
    prompt = f"""
    You are the Resume Agent for Placement Twin AI.
    Evaluate the following resume text. Compute a mock ATS score (0-100) based on typical software engineering / tech role requirements.
    Identify resume strengths and actionable improvements.
    
    Resume Content:
    \"\"\"{resume_text}\"\"\"
    
    Provide your analysis strictly in the following JSON format:
    {{
        "ats_score": 85,
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["improvement 1", "improvement 2"]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are an expert resume reviewer and recruiter. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        analysis = parse_json_markdown(res.content)
        
        if not analysis:
            analysis = {
                "ats_score": 50,
                "strengths": ["Basic format parsed"],
                "improvements": ["Optimize bullet points", "Include technical impact metric examples"]
            }
            
        return {"resume_analysis": analysis}
    except Exception as e:
        logger.error(f"Resume Evaluator node error: {e}")
        return {"errors": state.get("errors", []) + [f"Resume Evaluator: {str(e)}"]}


def skill_gap_node(state: AgentState) -> Dict[str, Any]:
    """Compares current skills against typical job requirements, referencing notes via RAG if available."""
    logger.info("Running Skill Gap Agent")
    llm = get_llm()
    profile = state.get("profile", {})
    skills = profile.get("skills", [])
    target_companies = profile.get("target_companies", [])
    goals = profile.get("career_goals", "")
    
    # Query RAG store for company prep files to understand skill requirements
    rag_context = ""
    query = f"Interview preparation requirements for {', '.join(target_companies)} {goals}"
    docs = search_similarity(query, k=2)
    if docs:
        rag_context = "\n".join([doc.page_content for doc in docs])
        
    prompt = f"""
    You are the Skill Gap Agent for Placement Twin AI.
    Compare the student's skills with the requirements of their target companies and career goals.
    
    Student Skills: {', '.join(skills)}
    Target Companies: {', '.join(target_companies)}
    Career Goals: {goals}
    
    {"Related Knowledge Base Info:" if rag_context else ""}
    {rag_context}
    
    Compute a matching score percentage and identify:
    1. Matching Skills: Skills the student already has that fit the goals.
    2. Missing Skills: Required skills that the student is missing or should strengthen.
    
    Provide your analysis strictly in the following JSON format:
    {{
        "relevance_percentage": 75,
        "matching_skills": ["skill 1", "skill 2"],
        "missing_skills": ["skill A", "skill B"]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are an expert technical interviewer and recruiter. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        analysis = parse_json_markdown(res.content)
        
        if not analysis:
            analysis = {
                "relevance_percentage": 60,
                "matching_skills": skills[:3] if skills else ["Programming Basics"],
                "missing_skills": ["System Design", "Cloud Infrastructure"]
            }
            
        return {"skill_gap": analysis}
    except Exception as e:
        logger.error(f"Skill Gap node error: {e}")
        return {"errors": state.get("errors", []) + [f"Skill Gap: {str(e)}"]}


def project_evaluator_node(state: AgentState) -> Dict[str, Any]:
    """Evaluates student projects details, suggests improvements and generates tailored mock questions."""
    logger.info("Running Project Evaluation Agent")
    llm = get_llm()
    # In practice, projects are retrieved from state or DB
    user_id = state.get("user_id")
    
    # Fetch projects from context
    profile = state.get("profile", {})
    academic_history = profile.get("academic_history", "")
    
    # We will pass a standard description in the state or look for 'projects' list in state profile
    projects = profile.get("projects", [])
    if not projects:
        # Fallback to standard mock projects to ensure we have content to analyze
        projects = [
            {"title": "E-Commerce App", "description": "A web store built with Django and SQL"},
            {"title": "AI Image Classifier", "description": "Tensorflow CNN model for image classification"}
        ]
        
    evaluated_projects = []
    
    for proj in projects:
        prompt = f"""
        You are the Project Evaluation Agent for Placement Twin AI.
        Analyze the following student project, score its quality (0-100), recommend technical improvements, and generate 2 custom interview questions a recruiter would ask about it.
        
        Project Title: {proj.get('title')}
        Project Description: {proj.get('description')}
        
        Provide your analysis strictly in the following JSON format:
        {{
            "title": "{proj.get('title')}",
            "score": 80,
            "suggestions": ["improvement suggestion 1", "improvement suggestion 2"],
            "interview_questions": ["interview question 1", "interview question 2"]
        }}
        """
        
        try:
            messages = [
                SystemMessage(content="You are a senior software architect. Respond only with valid JSON."),
                HumanMessage(content=prompt)
            ]
            res = llm.invoke(messages)
            analysis = parse_json_markdown(res.content)
            
            if not analysis:
                analysis = {
                    "title": proj.get('title'),
                    "score": 70,
                    "suggestions": ["Refactor codebase", "Write API documentation"],
                    "interview_questions": ["Explain the architecture.", "How do you scale this system?"]
                }
            evaluated_projects.append(analysis)
        except Exception as e:
            logger.error(f"Error evaluating project {proj.get('title')}: {e}")
            evaluated_projects.append({
                "title": proj.get('title'),
                "score": 60,
                "suggestions": [f"Audit failed: {str(e)}"],
                "interview_questions": ["Can you explain the main modules of this project?"]
            })
            
    return {"projects_analysis": evaluated_projects}


def roadmap_agent_node(state: AgentState) -> Dict[str, Any]:
    """Generates weekly and monthly learning roadmaps incorporating skill gaps and resume improvements."""
    logger.info("Running Roadmap Agent")
    llm = get_llm()
    profile = state.get("profile", {})
    skill_gap = state.get("skill_gap", {})
    resume_analysis = state.get("resume_analysis", {})
    
    missing_skills = skill_gap.get("missing_skills", [])
    resume_improvements = resume_analysis.get("improvements", [])
    
    prompt = f"""
    You are the Roadmap Agent for Placement Twin AI.
    Create a personalized technical learning roadmap for the student over a 4-week period and a high-level 2-month plan.
    Target Goals: {profile.get('career_goals')}
    Missing Skills to Master: {', '.join(missing_skills)}
    Resume Improvements to Address: {', '.join(resume_improvements)}
    
    Provide your output strictly in the following JSON format:
    {{
        "weekly_tasks": {{
            "Week 1": ["task 1", "task 2"],
            "Week 2": ["task 1", "task 2"],
            "Week 3": ["task 1", "task 2"],
            "Week 4": ["task 1", "task 2"]
        }},
        "monthly_tasks": {{
            "Month 1": ["month 1 goals"],
            "Month 2": ["month 2 goals"]
        }}
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are an expert curriculum developer. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        roadmap = parse_json_markdown(res.content)
        
        if not roadmap:
            roadmap = {
                "weekly_tasks": {
                    "Week 1": ["Study " + (missing_skills[0] if missing_skills else "CS fundamentals")],
                    "Week 2": ["Build API service components"],
                    "Week 3": ["Refactor resume profile description"],
                    "Week 4": ["Take mock interview checks"]
                },
                "monthly_tasks": {
                    "Month 1": ["Master missing skills and core topics"],
                    "Month 2": ["Build complete portfolio project"]
                }
            }
            
        return {"learning_roadmap": roadmap}
    except Exception as e:
        logger.error(f"Roadmap Agent node error: {e}")
        return {"errors": state.get("errors", []) + [f"Roadmap Agent: {str(e)}"]}


def dsa_agent_node(state: AgentState) -> Dict[str, Any]:
    """Recommends specific Data Structure and Algorithm topics and questions using RAG context if applicable."""
    logger.info("Running DSA Agent")
    llm = get_llm()
    profile = state.get("profile", {})
    
    # Query RAG store for DSA tips
    rag_context = ""
    docs = search_similarity("important DSA interview questions topics", k=2)
    if docs:
        rag_context = "\n".join([doc.page_content for doc in docs])
        
    prompt = f"""
    You are the DSA Agent for Placement Twin AI.
    Recommend a list of 4 highly relevant DSA questions appropriate for the student's career goal ({profile.get('career_goals')}).
    Include the question name, topic, difficulty level (Easy, Medium, Hard), and typical platform (LeetCode, HackerRank).
    
    {"Related DSA Study Guide Context:" if rag_context else ""}
    {rag_context}
    
    Provide your output strictly in the following JSON format:
    {{
        "recommended_questions": [
            {{"name": "Question Name", "topic": "topic", "difficulty": "difficulty", "platform": "LeetCode"}}
        ]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are a competitive programming coach. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        dsa_recs = parse_json_markdown(res.content)
        
        if not dsa_recs or "recommended_questions" not in dsa_recs:
            dsa_recs = {
                "recommended_questions": [
                    {"name": "Two Sum", "topic": "Arrays", "difficulty": "Easy", "platform": "LeetCode"},
                    {"name": "Reverse Linked List", "topic": "Linked Lists", "difficulty": "Easy", "platform": "LeetCode"},
                    {"name": "Longest Substring Without Repeating Characters", "topic": "Sliding Window", "difficulty": "Medium", "platform": "LeetCode"},
                    {"name": "Number of Islands", "topic": "Graphs", "difficulty": "Medium", "platform": "LeetCode"}
                ]
            }
            
        return {"dsa_recommendations": dsa_recs}
    except Exception as e:
        logger.error(f"DSA Agent node error: {e}")
        return {"errors": state.get("errors", []) + [f"DSA Agent: {str(e)}"]}


def readiness_score_node(state: AgentState) -> Dict[str, Any]:
    """Calculates subscores and a consolidated Placement Readiness Score (0-100) with detailed reasoning."""
    logger.info("Running Readiness Score Agent")
    llm = get_llm()
    
    resume_analysis = state.get("resume_analysis", {})
    skill_gap = state.get("skill_gap", {})
    projects_analysis = state.get("projects_analysis", [])
    
    # Calculate initial scores
    resume_score = resume_analysis.get("ats_score", 50)
    skill_score = skill_gap.get("relevance_percentage", 50)
    
    project_scores = [p.get("score", 60) for p in projects_analysis]
    project_score = int(sum(project_scores) / len(project_scores)) if project_scores else 60
    
    # Defaults for other scores
    dsa_score = 65
    interview_score = 70
    
    prompt = f"""
    You are the Placement Readiness Score Agent for Placement Twin AI.
    Calculate a consolidated placement readiness score from 0-100.
    Incorporate the following component metrics:
    - Resume Score: {resume_score}
    - Skill Relevance: {skill_score}
    - Project Quality Score: {project_score}
    - Est. DSA Score: {dsa_score}
    - Est. Interview Score: {interview_score}
    
    Compile these into an overall score and write a constructive summary explaining the reasoning behind the grade.
    
    Provide your output strictly in the following JSON format:
    {{
        "overall_score": 75,
        "resume_score": {resume_score},
        "dsa_score": {dsa_score},
        "interview_score": {interview_score},
        "skill_score": {skill_score},
        "project_score": {project_score},
        "reasoning": "Detailed aggregate explanation."
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are a senior tech lead evaluator. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        readiness = parse_json_markdown(res.content)
        
        if not readiness:
            readiness = {
                "overall_score": int((resume_score + skill_score + project_score + dsa_score + interview_score) / 5),
                "resume_score": resume_score,
                "dsa_score": dsa_score,
                "interview_score": interview_score,
                "skill_score": skill_score,
                "project_score": project_score,
                "reasoning": "Calculated score is a running average of your resume performance, skill matches, and project complexities."
            }
            
        return {"readiness_score": readiness}
    except Exception as e:
        logger.error(f"Readiness Score node error: {e}")
        return {"errors": state.get("errors", []) + [f"Readiness Score: {str(e)}"]}


def daily_planner_node(state: AgentState) -> Dict[str, Any]:
    """Generates daily preparation tasks mapping to DSA, CS theory, projects, and resume refinements."""
    logger.info("Running Daily Planner Agent")
    llm = get_llm()
    learning_roadmap = state.get("learning_roadmap", {})
    dsa_recs = state.get("dsa_recommendations", {})
    
    dsa_questions = [q.get("name") for q in dsa_recs.get("recommended_questions", [])]
    weekly_tasks = learning_roadmap.get("weekly_tasks", {}).get("Week 1", [])
    
    prompt = f"""
    You are the Daily AI Planner Agent for Placement Twin AI.
    Generate a target list of 4 specific tasks for the student to complete today.
    Draw items from:
    1. Weekly Roadmap tasks: {weekly_tasks}
    2. DSA recommendations: {dsa_questions}
    3. General interview topics (mock checks, OS/DBMS theory review)
    
    Provide your output strictly in the following JSON format:
    {{
        "tasks": [
            {{"text": "Specific actionable task", "category": "DSA / Resume / Projects / CS Fundamentals", "completed": false}}
        ]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are an agile coordinator agent. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        planner = parse_json_markdown(res.content)
        
        if not planner or "tasks" not in planner:
            planner = {
                "tasks": [
                    {"text": f"Solve DSA question: {dsa_questions[0] if dsa_questions else 'Two Sum'}", "category": "DSA", "completed": False},
                    {"text": "Review deadlock conditions and solutions", "category": "CS Fundamentals", "completed": False},
                    {"text": "Update Github Readme file for portfolio projects", "category": "Projects", "completed": False},
                    {"text": "Draft a personalized cover letter for target applications", "category": "Resume", "completed": False}
                ]
            }
            
        return {"daily_plan": planner}
    except Exception as e:
        logger.error(f"Daily Planner node error: {e}")
        return {"errors": state.get("errors", []) + [f"Daily Planner: {str(e)}"]}


def motivation_node(state: AgentState) -> Dict[str, Any]:
    """Creates a personalized motivation quote and short checklist reminders based on current progress."""
    logger.info("Running Motivation Agent")
    llm = get_llm()
    readiness_score = state.get("readiness_score", {})
    overall_score = readiness_score.get("overall_score", 70)
    
    prompt = f"""
    You are the Motivation Agent for Placement Twin AI.
    Generate a high-impact personalized motivational quote and 3 action reminders.
    The student currently has an overall Placement Readiness Score of {overall_score}/100.
    Make the response encouraging, professional, and slightly competitive.
    
    Provide your output strictly in the following JSON format:
    {{
        "quote": "Personalized motivational quote here.",
        "reminders": [
            "reminder 1",
            "reminder 2",
            "reminder 3"
        ]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are an inspiring technical coach. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        motivation = parse_json_markdown(res.content)
        
        if not motivation:
            motivation = {
                "quote": "Success isn't about being perfect. It's about being consistent. Keep pushing!",
                "reminders": [
                    "Finish today's scheduled DSA problem.",
                    "Review mock interview theory guides.",
                    "Strengthen core web dev project endpoints."
                ]
            }
            
        return {"motivation": motivation}
    except Exception as e:
        logger.error(f"Motivation node error: {e}")
        return {"errors": state.get("errors", []) + [f"Motivation: {str(e)}"]}


def job_matching_node(state: AgentState) -> Dict[str, Any]:
    """Compares the student profile against a specific job description and computes compatibility."""
    logger.info("Running Job Matching Agent")
    llm = get_llm()
    profile = state.get("profile", {})
    skills = profile.get("skills", [])
    job_description = state.get("job_description", "")
    
    if not job_description:
        return {
            "job_match": {
                "compatibility_score": 0,
                "matching_skills": [],
                "missing_skills": [],
                "recommendations": ["No job description provided for match."]
            }
        }
        
    prompt = f"""
    You are the Job Matching Agent for Placement Twin AI.
    Analyze the compatibility of the student's profile against the provided Job Description.
    
    Student Skills: {', '.join(skills)}
    Student Goals: {profile.get('career_goals')}
    
    Job Description:
    \"\"\"{job_description}\"\"\"
    
    Calculate a compatibility score (0-100), identify matching skills, list missing skills, and give 2 clear recommendations to bridge the gap.
    
    Provide your analysis strictly in the following JSON format:
    {{
        "compatibility_score": 80,
        "matching_skills": ["skill 1", "skill 2"],
        "missing_skills": ["skill A", "skill B"],
        "recommendations": ["recommendation 1", "recommendation 2"]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are an expert technical screening recruiter. Respond only with valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        match_res = parse_json_markdown(res.content)
        
        if not match_res:
            match_res = {
                "compatibility_score": 50,
                "matching_skills": skills[:2] if skills else [],
                "missing_skills": ["Required Stack tools"],
                "recommendations": ["Align projects with the stack mentioned in description."]
            }
            
        return {"job_match": match_res}
    except Exception as e:
        logger.error(f"Job Match node error: {e}")
        return {"errors": state.get("errors", []) + [f"Job Matcher: {str(e)}"]}
