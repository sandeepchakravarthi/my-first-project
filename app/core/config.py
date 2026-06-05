from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: Optional[str] = ""
    OPENAI_API_KEY: Optional[str] = ""
    TAVILY_API_KEY: Optional[str] = ""
    REDIS_URL: str = "redis://localhost:6379"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    SESSION_TTL: int = 3600  # 1 hour

    class Config:
        env_file = ".env"

settings = Settings()
