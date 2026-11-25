from fastapi import APIRouter
from app.api.endpoints import auth, profile, roadmap, project, interview, planner, rag

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["Student Profile"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Roadmap & DSA"])
api_router.include_router(project.router, prefix="/projects", tags=["Project Evaluation"])
api_router.include_router(interview.router, prefix="/interview", tags=["Mock Interview"])
api_router.include_router(planner.router, prefix="/planner", tags=["Daily Planner"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG Management"])
