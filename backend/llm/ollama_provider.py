import httpx
from typing import AsyncIterator
from backend.llm.base_provider import BaseProvider
from backend.config.settings import settings


class OllamaProvider(BaseProvider):

    def __init__(self):

        self.base_url = settings.OLLAMA_BASE_URL

        self.model = settings.OLLAMA_MODEL

        self.timeout = settings.get_provider_timeout("ollama")

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2,
    ):

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                },
            },
            timeout=self.timeout,
        )

        data = response.json()

        return data.get("response", "")

    async def stream(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": temperature
                    },
                },
                timeout=self.timeout,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk
