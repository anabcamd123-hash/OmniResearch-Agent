import os
from openai import OpenAI


class DeepSeekProvider:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2
    ):

        response = (
            self.client.chat.completions.create(
                model="deepseek-chat",
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
