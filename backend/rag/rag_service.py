from backend.storage.repository import MemoryRepository
from backend.rag.retriever import Retriever
from backend.utils.logger import logger


class RAGService:

    def __init__(self):

        self.memory_repo = MemoryRepository()

        self.retriever = Retriever()

    async def build_index(self):

        logger.info(
            "[RAG] Building index from memory..."
        )

        memories = await self.memory_repo.get_recent(
            limit=1000
        )

        count = 0
        for m in memories:

            content = m["content"]

            if content and len(content) > 10:
                self.retriever.add_document(
                    content
                )
                count += 1

        logger.info(
            f"[RAG] Index built: {count} documents"
        )

    async def query(
        self,
        question: str,
        top_k: int = 5,
    ):

        results = self.retriever.retrieve(
            question, top_k
        )

        return results

    async def add(self, text: str):

        if text and len(text) > 10:
            self.retriever.add_document(text)


rag_service = RAGService()
