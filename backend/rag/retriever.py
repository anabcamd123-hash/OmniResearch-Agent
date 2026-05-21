from backend.rag.embedder import Embedder
from backend.rag.vector_store import VectorStore


class Retriever:

    def __init__(self):

        self.embedder = Embedder()

        self.vector_store = VectorStore(
            dim=384
        )

    def add_document(self, text: str):

        vec = self.embedder.encode(text)

        self.vector_store.add(vec, text)

    def retrieve(self, query: str, top_k=5):

        vec = self.embedder.encode(query)

        return self.vector_store.search(
            vec, top_k
        )

    def clear(self):

        self.vector_store.clear()
