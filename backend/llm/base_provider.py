from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseProvider(ABC):

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2,
    ):
        pass

    async def stream(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:

        yield self.invoke(prompt, temperature)
