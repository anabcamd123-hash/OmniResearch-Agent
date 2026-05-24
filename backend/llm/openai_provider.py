import os
from openai import OpenAI
from typing import AsyncIterator
from backend.llm.base_provider import BaseProvider
from backend.config.settings import settings


class OpenAIProvider(BaseProvider):

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            timeout=settings.get_provider_timeout("openai"),
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2,
    ):

        response = (
            self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )

    async def stream(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:

        response = (
            self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=True,
            )
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
