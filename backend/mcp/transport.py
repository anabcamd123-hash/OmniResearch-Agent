from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class MCPTransport(ABC):

    @abstractmethod
    async def connect(self, server_url: str):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def send(
        self,
        method: str,
        params: dict,
    ) -> Any:
        pass


class HTTPTransport(MCPTransport):

    def __init__(self):
        self.server_url = None
        self.client = None

    async def connect(self, server_url: str):
        import httpx
        self.server_url = server_url
        self.client = httpx.AsyncClient()

    async def disconnect(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def send(
        self,
        method: str,
        params: dict,
    ) -> Any:

        if not self.client:
            raise RuntimeError("Not connected")

        response = await self.client.post(
            f"{self.server_url}/{method}",
            json=params,
            timeout=300,
        )

        response.raise_for_status()

        return response.json()
