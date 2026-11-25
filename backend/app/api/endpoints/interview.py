import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.api.endpoints.auth import get_current_user
from app.models.domain import User, MockInterview, Profile
from app.models.schemas import MockInterviewCreate, MockInterviewResponse
from app.services.agents.llm import get_llm
from app.services.rag.vector_store import search_similarity
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.agents.nodes.agent_nodes import parse_json_markdown

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=List[MockInterviewResponse])
def list_interviews(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """Retrieve list of previous mock interviews for the student."""
    interviews = session.exec(select(MockInterview).where(MockInterview.user_id == current_user.id)).all()
    return interviews


@router.post("/start")
def start_interview(
    setup: MockInterviewCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Start a new mock interview session and generate the first question."""
    llm = get_llm()
    profile = session.exec(select(Profile).where(Profile.user_id == current_user.id)).first()
    skills = profile.skills if profile else []
    
    # Query RAG for CS fundamental context related to the interview topic/role
    rag_context = ""
    docs = search_similarity(f"interview questions for {setup.job_role} {setup.interview_type}", k=2)
    if docs:
        rag_context = "\n".join([doc.page_content for doc in docs])
        
    prompt = f"""
    You are the Interview Coach Agent for Placement Twin AI.
    Generate the first question for a {setup.interview_type} mock interview for a student targeting a {setup.job_role} position.
    
    Student Skills: {', '.join(skills)}
    {"Related preparation guides:" if rag_context else ""}
    {rag_context}
    
    Make the question realistic, professional, and targeted. Ask a single question.
    Provide your output strictly in the following JSON format:
    {{
        "question": "The interview question text here."
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are a professional technical recruiter. Respond only in valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        res_json = parse_json_markdown(res.content)
        question = res_json.get("question", f"Can you introduce yourself and explain your interest in the {setup.job_role} role?")
    except Exception as e:
        logger.error(f"Error starting mock interview: {e}")
        question = f"Tell me about a challenging project you built using your skills: {', '.join(skills) if skills else 'programming'}."
        
    new_interview = MockInterview(
        user_id=current_user.id,
        job_role=setup.job_role,
        interview_type=setup.interview_type,
        score=0,
        feedback={},
        transcript=[{"speaker": "Interviewer", "text": question}]
    )
    
    session.add(new_interview)
    session.commit()
    session.refresh(new_interview)
    
    return {
        "interview_id": new_interview.id,
        "question": question
    }


@router.post("/{interview_id}/answer")
def submit_answer(
    interview_id: int,
    payload: Dict[str, str], # {"answer": "student answer"}
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit the student's answer to the last question. Returns brief feedback and the next question."""
    interview = session.exec(
        select(MockInterview).where(
            (MockInterview.id == interview_id) & (MockInterview.user_id == current_user.id)
        )
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    student_answer = payload.get("answer", "")
    if not student_answer:
        raise HTTPException(status_code=400, detail="Answer string is required.")
        
    transcript = interview.transcript
    # Identify last question asked
    last_question = ""
    for turn in reversed(transcript):
        if turn["speaker"] == "Interviewer":
            last_question = turn["text"]
            break
            
    # Append student answer
    transcript.append({"speaker": "Student", "text": student_answer})
    
    # Assess answer and ask next question (limit interview to 3 questions for fast mock iterations)
    question_count = sum(1 for turn in transcript if turn["speaker"] == "Interviewer")
    
    llm = get_llm()
    
    if question_count >= 3:
        # Wrap up interview
        prompt = f"""
        Evaluate the student's final answer and wrap up the interview.
        Last Question: {last_question}
        Student Answer: {student_answer}
        
        Provide a friendly wrapping message stating that the mock interview is complete.
        Provide your output strictly in the following JSON format:
        {{
            "feedback": "Brief feedback on the answer.",
            "next_question": "Interview complete. Click 'Finish' to view detailed analytics and performance score.",
            "is_complete": true
        }}
        """
    else:
        prompt = f"""
        Evaluate the student's answer and generate the next question.
        Last Question: {last_question}
        Student Answer: {student_answer}
        Role: {interview.job_role} ({interview.interview_type} interview)
        
        Provide your output strictly in the following JSON format:
        {{
            "feedback": "Constructive feedback on the student's answer (1-2 sentences).",
            "next_question": "The next interview question.",
            "is_complete": false
        }}
        """
        
    try:
        messages = [
            SystemMessage(content="You are a professional technical recruiter. Respond only in valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        res_json = parse_json_markdown(res.content)
        
        feedback = res_json.get("feedback", "Good attempt.")
        next_question = res_json.get("next_question", "Next question.")
        is_complete = res_json.get("is_complete", False)
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        feedback = "Answer logged."
        next_question = "Can you elaborate on your experience with system scaling or testing?"
        is_complete = False
        
    transcript.append({"speaker": "Interviewer", "text": next_question})
    
    # Update DB
    interview.transcript = transcript
    session.add(interview)
    session.commit()
    
    return {
        "feedback": feedback,
        "next_question": next_question,
        "is_complete": is_complete
    }


@router.post("/{interview_id}/finish", response_model=MockInterviewResponse)
def finish_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Ends the interview, evaluates the entire transcript, computes final score and detailed report."""
    interview = session.exec(
        select(MockInterview).where(
            (MockInterview.id == interview_id) & (MockInterview.user_id == current_user.id)
        )
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    llm = get_llm()
    transcript_str = "\n".join([f"{t['speaker']}: {t['text']}" for t in interview.transcript])
    
    prompt = f"""
    You are the Interview Coach Agent for Placement Twin AI.
    Evaluate the following complete mock interview transcript for the role: {interview.job_role} ({interview.interview_type} interview).
    Assign a final score (0-100) and draft a detailed feedback report outlining strengths, weaknesses, and concrete recommendations.
    
    Transcript:
    \"\"\"{transcript_str}\"\"\"
    
    Provide your output strictly in the following JSON format:
    {{
        "score": 78,
        "strengths": ["list of strengths"],
        "weaknesses": ["list of weaknesses"],
        "suggestions": ["specific recommendations to improve"]
    }}
    """
    
    try:
        messages = [
            SystemMessage(content="You are a senior tech recruiter and performance evaluator. Respond only in valid JSON."),
            HumanMessage(content=prompt)
        ]
        res = llm.invoke(messages)
        report = parse_json_markdown(res.content)
        
        score = report.get("score", 70)
        feedback = {
            "strengths": report.get("strengths", ["Good structure"]),
            "weaknesses": report.get("weaknesses", ["Expand on technical details"]),
            "suggestions": report.get("suggestions", ["Practice system design"])
        }
    except Exception as e:
        logger.error(f"Error wrapping up interview: {e}")
        score = 65
        feedback = {
            "strengths": ["Completed interview successfully"],
            "weaknesses": ["Analysis failed to generate"],
            "suggestions": ["Try running again with active internet connections"]
        }
        
    interview.score = score
    interview.feedback = feedback
    session.add(interview)
    session.commit()
    session.refresh(interview)
    
    return interview
