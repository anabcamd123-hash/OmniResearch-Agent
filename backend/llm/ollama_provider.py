import requests
from backend.llm.base_provider import BaseProvider
from backend.config.settings import settings


class OllamaProvider(BaseProvider):

    def __init__(self):

        self.base_url = settings.OLLAMA_BASE_URL

        self.model = settings.OLLAMA_MODEL

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2,
    ):

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                },
            },
            timeout=300,
        )

        data = response.json()

        return data.get("response", "")
