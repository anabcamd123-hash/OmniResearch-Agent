import os
import requests
from backend.llm.base_provider import BaseProvider


class GeminiProvider(BaseProvider):

    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        self.base_url = (
            "https://generativelanguage.googleapis.com"
            "/v1beta/models/gemini-2.0-flash"
            ":generateContent"
        )

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2
    ):

        url = (
            f"{self.base_url}"
            f"?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }

        response = requests.post(
            url, json=payload
        )

        data = response.json()

        return (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )
