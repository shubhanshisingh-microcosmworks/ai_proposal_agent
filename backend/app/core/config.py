import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    PROJECT_NAME: str = "AI Proposal Agent"
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_proposal_agent_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "2c06faae23cf6b334fcb985e8e743d1bb9aa51fc61fdc20d7274f77986e5520a")

    class Config:
        case_sensitive = True

settings = Settings()