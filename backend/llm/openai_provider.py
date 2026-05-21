import os
from openai import OpenAI
from backend.llm.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2
    ):

        response = (
            self.client.chat.completions.create(
                model="gpt-4.1-mini",
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
