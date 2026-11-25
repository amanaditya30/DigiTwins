import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    # Server configuration
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "e83a216fcbca253cf91648a73a62886f3b06de15c7a52e9f1a26d70d235c3bc2")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./placement_twin.db")

    # LLM Providers
    PRIMARY_LLM_PROVIDER: str = os.getenv("PRIMARY_LLM_PROVIDER", "openai").lower()
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama3-70b-8192")

    # ChromaDB
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./data/chromadb")
    KNOWLEDGE_SOURCES_DIR: str = os.getenv("KNOWLEDGE_SOURCES_DIR", "./knowledge_sources")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

settings = Settings()
