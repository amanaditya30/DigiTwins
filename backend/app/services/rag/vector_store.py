import os
import logging
from typing import List
from langchain_core.documents import Document
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import embedding options
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    Chroma = None


class FallbackEmbeddings:
    """A dummy embedding class that generates fake embeddings if no external models are available."""
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Return simple dummy floats matching standard dimension (384)
        return [[0.0] * 384 for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return [0.0] * 384


def get_embedding_function():
    """Retrieve embedding model based on configuration, with fallback."""
    if settings.PRIMARY_LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        if OpenAIEmbeddings is not None:
            try:
                return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAIEmbeddings: {e}. Falling back...")
    
    if HuggingFaceEmbeddings is not None:
        try:
            # Prevent downloads failing the startup by wrapping in try/except
            # Set local_files_only = False or let it download automatically
            return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
        except Exception as e:
            logger.warning(f"Failed to initialize HuggingFaceEmbeddings: {e}. Using local fallback mock embeddings.")
            
    return FallbackEmbeddings()


def get_vector_store(collection_name: str = "placement_notes"):
    """Initialize or load a Chroma vector store."""
    embeddings = get_embedding_function()
    
    # Ensure data directory exists
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    
    if Chroma is not None:
        try:
            return Chroma(
                persist_directory=settings.CHROMA_DB_DIR,
                embedding_function=embeddings,
                collection_name=collection_name
            )
        except Exception as e:
            logger.error(f"Error loading Chroma DB: {e}")
            return None
    else:
        logger.warning("Chroma is not installed. RAG search will not operate correctly.")
        return None


def add_documents_to_store(documents: List[Document], collection_name: str = "placement_notes") -> bool:
    """Ingest a list of langchain Documents into ChromaDB."""
    db = get_vector_store(collection_name)
    if db is not None:
        try:
            db.add_documents(documents)
            # In older langchain versions persist was needed; now it is auto-persisted.
            if hasattr(db, "persist"):
                db.persist()
            return True
        except Exception as e:
            logger.error(f"Failed to save documents to vector store: {e}")
            return False
    return False


def search_similarity(query: str, k: int = 4, collection_name: str = "placement_notes") -> List[Document]:
    """Retrieve k most similar documents from Chroma DB."""
    db = get_vector_store(collection_name)
    if db is not None:
        try:
            return db.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    return []
