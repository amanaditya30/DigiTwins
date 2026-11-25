from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread=False for multi-threaded access in FastAPI
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

def init_db():
    """Import all models so they register on metadata and create tables."""
    # Import domain models to ensure they are registered with SQLModel metadata
    from app.models.domain import User, Profile, DSAProgress, MockInterview, Project, Roadmap, DailyPlan, ReadinessScore
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency generator for database sessions."""
    with Session(engine) as session:
        yield session
