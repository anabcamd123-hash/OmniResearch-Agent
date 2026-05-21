from backend.config.settings import settings
from backend.llm.base_provider import BaseProvider
from backend.llm.openai_provider import OpenAIProvider
from backend.llm.gemini_provider import GeminiProvider
from backend.llm.deepseek_provider import DeepSeekProvider
from backend.llm.ollama_provider import OllamaProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
    "ollama": OllamaProvider,
}

_provider_instance = None


def get_provider():

    global _provider_instance

    if _provider_instance:
        return _provider_instance

    provider_name = settings.MODEL_PROVIDER.lower()

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available: {list(PROVIDERS.keys())}"
        )

    _provider_instance = PROVIDERS[provider_name]()

    return _provider_instance
