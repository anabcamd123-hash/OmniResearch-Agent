from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        temperature: float = 0.2,
    ):
        pass
