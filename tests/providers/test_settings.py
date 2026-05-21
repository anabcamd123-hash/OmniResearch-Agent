import pytest
from backend.config.settings import settings


def test_settings_defaults():

    assert settings.MODEL_PROVIDER in [
        "openai", "gemini", "deepseek", "ollama"
    ]
    assert settings.RAG_TOP_K == 5
    assert settings.OLLAMA_BASE_URL is not None


def test_settings_database_url():

    assert "sqlite" in settings.DATABASE_URL
