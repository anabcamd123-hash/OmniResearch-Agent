import os
from backend.llm.base_provider import BaseProvider
from backend.llm.openai_provider import OpenAIProvider
from backend.llm.gemini_provider import GeminiProvider
from backend.llm.deepseek_provider import DeepSeekProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
}

_provider_instance = None


def get_provider():

    global _provider_instance

    if _provider_instance:
        return _provider_instance

    provider_name = os.getenv(
        "MODEL_PROVIDER", "openai"
    ).lower()

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available: {list(PROVIDERS.keys())}"
        )

    _provider_instance = PROVIDERS[provider_name]()

    return _provider_instance
