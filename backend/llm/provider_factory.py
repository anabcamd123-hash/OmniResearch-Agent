import os
from backend.llm.openai_provider import OpenAIProvider
from backend.llm.gemini_provider import GeminiProvider
from backend.llm.deepseek_provider import DeepSeekProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider
}


def get_provider():

    provider_name = os.getenv(
        "MODEL_PROVIDER", "openai"
    ).lower()

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available: {list(PROVIDERS.keys())}"
        )

    return PROVIDERS[provider_name]()
