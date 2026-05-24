from backend.storage.repository import MemoryRepository
from backend.rag.retriever import Retriever
from backend.utils.logger import logger


class RAGService:

    def __init__(self):

        self.memory_repo = MemoryRepository()

        self.retriever = Retriever()

    async def build_index(self):

        logger.info(
            "[RAG] Building index from "
            "learning memories..."
        )

        try:
            memories = (
                await self.memory_repo.get_learning_memories(
                    limit=2000
                )
            )
        except Exception as e:
            logger.warning(
                f"[RAG] Failed to load memories: {e}"
            )
            return

        count = 0
        for m in memories:

            content = m["content"]

            if content and len(content) > 10:
                try:
                    self.retriever.add_document(
                        content
                    )
                    count += 1
                except Exception:
                    pass

        logger.info(
            f"[RAG] Index built: "
            f"{count} learning memories"
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
