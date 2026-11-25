from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# ----------------- Auth Schemas -----------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

# ----------------- Profile Schemas -----------------

class ProfileCreate(BaseModel):
    full_name: str
    skills: List[str]
    interests: List[str]
    target_companies: List[str]
    career_goals: str
    academic_history: str
    resume_text: Optional[str] = ""

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    career_goals: Optional[str] = None
    academic_history: Optional[str] = None
    resume_text: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    skills: List[str]
    interests: List[str]
    target_companies: List[str]
    career_goals: str
    academic_history: str
    resume_filename: Optional[str]
    updated_at: datetime

    class Config:
        orm_mode = True

# ----------------- DSA Schemas -----------------

class DSAProgressCreate(BaseModel):
    topic: str
    question_name: str
    difficulty: str
    status: str

class DSAProgressUpdate(BaseModel):
    status: str

class DSAProgressResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    question_name: str
    difficulty: str
    status: str
    solved_at: Optional[datetime]

    class Config:
        orm_mode = True

# ----------------- Mock Interview Schemas -----------------

class MockInterviewCreate(BaseModel):
    job_role: str
    interview_type: str

class MockInterviewResponse(BaseModel):
    id: int
    user_id: int
    job_role: str
    interview_type: str
    score: int
    feedback: Dict[str, Any]
    transcript: List[Dict[str, str]]
    created_at: datetime

    class Config:
        orm_mode = True

class InterviewQuestionRequest(BaseModel):
    role: str
    topic: str
    question: str
    answer: str

# ----------------- Project Schemas -----------------

class ProjectCreate(BaseModel):
    title: str
    description: str
    repo_url: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    repo_url: Optional[str]
    score: int
    suggestions: List[str]
    interview_questions: List[str]

    class Config:
        orm_mode = True

# ----------------- Daily Plan Schemas -----------------

class DailyPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_date: date
    tasks: List[Dict[str, Any]]
    completed_tasks: List[str]

    class Config:
        orm_mode = True

# ----------------- Job Match Schemas -----------------

class JobMatchRequest(BaseModel):
    job_description: str

class JobMatchResponse(BaseModel):
    compatibility_score: int
    matching_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]
