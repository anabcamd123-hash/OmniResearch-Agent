from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── LLM ──────────────────────────────────────
    MODEL_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"

    # ── Database ─────────────────────────────────
    DATABASE_URL: str = (
        "sqlite+aiosqlite:///data/app.db"
    )
    REDIS_URL: str = "redis://localhost:6379"

    # ── RAG ──────────────────────────────────────
    RAG_TOP_K: int = 5

    # ── App ──────────────────────────────────────
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Tool Timeout ─────────────────────────────
    TOOL_TIMEOUT_DEFAULT: int = 30

    # ── Circuit Breaker ──────────────────────────
    BREAKER_THRESHOLD: int = 3
    BREAKER_RECOVERY_TIME: int = 60

    # ── Bulkhead (per agent/tool type) ───────────
    TOOL_LIMIT_GITHUB: int = 5
    TOOL_LIMIT_PDF: int = 2
    TOOL_LIMIT_RAG: int = 10
    TOOL_LIMIT_WEB: int = 5
    TOOL_LIMIT_PYTHON: int = 2

    BULKHEAD_RESEARCH: int = 5
    BULKHEAD_CODING: int = 3
    BULKHEAD_VERIFY: int = 2
    BULKHEAD_REFLECTION: int = 2

    @property
    def BULKHEAD_LIMIT(self) -> dict:
        return {
            "research": self.BULKHEAD_RESEARCH,
            "coding": self.BULKHEAD_CODING,
            "verify": self.BULKHEAD_VERIFY,
            "reflection": self.BULKHEAD_REFLECTION,
        }

    # ── Agent Timeout ────────────────────────────
    AGENT_TIMEOUT: int = 120

    # ── Provider Timeout ─────────────────────────
    OPENAI_TIMEOUT: int = 60
    GEMINI_TIMEOUT: int = 60
    DEEPSEEK_TIMEOUT: int = 60
    OLLAMA_TIMEOUT: int = 120

    @property
    def PROVIDER_TIMEOUT(self) -> dict:
        return {
            "openai": self.OPENAI_TIMEOUT,
            "gemini": self.GEMINI_TIMEOUT,
            "deepseek": self.DEEPSEEK_TIMEOUT,
            "ollama": self.OLLAMA_TIMEOUT,
        }

    def get_provider_timeout(
        self, provider: str = None
    ) -> int:
        provider = provider or self.MODEL_PROVIDER
        return self.PROVIDER_TIMEOUT.get(
            provider, 60
        )

    # ── Retry / DLQ ─────────────────────────────
    MAX_RETRY: int = 3
    RETRY_DELAY: int = 5
    DLQ_RETRY_INTERVAL: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
