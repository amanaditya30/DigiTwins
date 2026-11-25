import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.config import settings
from app.api.endpoints.auth import get_current_user
from app.models.domain import User
from app.services.rag.pipeline import ingest_documents_from_directory
from app.services.rag.vector_store import search_similarity

router = APIRouter()

@router.post("/upload")
def upload_knowledge_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload study notes (PDF or TXT) to the placement knowledge sources directory."""
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT documents are supported for RAG storage.")
        
    os.makedirs(settings.KNOWLEDGE_SOURCES_DIR, exist_ok=True)
    target_path = os.path.join(settings.KNOWLEDGE_SOURCES_DIR, file.filename)
    
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "message": "File uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")


@router.post("/ingest")
def trigger_ingestion(current_user: User = Depends(get_current_user)):
    """Triggers document processing: reads files from sources, splits them, generates embeddings, and saves to ChromaDB."""
    chunks_created = ingest_documents_from_directory()
    if chunks_created > 0:
        return {"message": f"Successfully ingested files. Created {chunks_created} vector chunks."}
    else:
        return {"message": "No new documents ingested. Seeded default mock study notes."}


@router.get("/search")
def search_knowledge_base(query: str, limit: int = 4, current_user: User = Depends(get_current_user)):
    """Search study notes database semantically for matching snippets."""
    docs = search_similarity(query, k=limit)
    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    return results
