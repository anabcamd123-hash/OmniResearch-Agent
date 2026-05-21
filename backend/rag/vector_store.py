import faiss
import numpy as np


class VectorStore:

    def __init__(self):

        self.index = faiss.IndexFlatL2(384)

        self.documents = []

    def add(
        self,
        vectors,
        chunks
    ):

        self.index.add(
            np.array(vectors)
        )

        self.documents.extend(chunks)

    def search(
        self,
        query_vector,
        k=3
    ):

        D, I = self.index.search(
            np.array([query_vector]),
            k
        )

        return [
            self.documents[i]
            for i in I[0]
            if i < len(self.documents)
        ]


vector_store = VectorStore()
