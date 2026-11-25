from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import String

# ----------------- Database Models -----------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    full_name: str
    skills: List[str] = Field(default=[], sa_column=Column(JSON))
    interests: List[str] = Field(default=[], sa_column=Column(JSON))
    target_companies: List[str] = Field(default=[], sa_column=Column(JSON))
    career_goals: str = Field(default="")
    academic_history: str = Field(default="")
    resume_text: str = Field(default="")
    resume_filename: Optional[str] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DSAProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    topic: str
    question_name: str
    difficulty: str  # "Easy", "Medium", "Hard"
    status: str = Field(default="Unsolved")  # "Solved", "In_Progress", "Unsolved"
    solved_at: Optional[datetime] = Field(default=None)

class MockInterview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    job_role: str
    interview_type: str  # "Technical", "HR"
    score: int = Field(default=0)  # 0 to 100
    feedback: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    transcript: List[Dict[str, str]] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: str
    repo_url: Optional[str] = Field(default=None)
    score: int = Field(default=0)
    suggestions: List[str] = Field(default=[], sa_column=Column(JSON))
    interview_questions: List[str] = Field(default=[], sa_column=Column(JSON))

class Roadmap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    weekly_tasks: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    monthly_tasks: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DailyPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    plan_date: date = Field(default_factory=date.today)
    tasks: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    completed_tasks: List[str] = Field(default=[], sa_column=Column(JSON))

class ReadinessScore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    overall_score: int = Field(default=0)
    resume_score: int = Field(default=0)
    dsa_score: int = Field(default=0)
    interview_score: int = Field(default=0)
    skill_score: int = Field(default=0)
    project_score: int = Field(default=0)
    reasoning: str = Field(default="")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
