from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # LLM
    MODEL_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"

    # Database
    DATABASE_URL: str = (
        "sqlite+aiosqlite:///data/app.db"
    )

    # RAG
    RAG_TOP_K: int = 5

    # App
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
