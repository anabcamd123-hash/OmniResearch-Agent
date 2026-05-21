import faiss
import numpy as np


class VectorStore:

    def __init__(self, dim: int = 384):

        self.index = faiss.IndexFlatL2(dim)

        self.texts = []

    def add(self, vector, text: str):

        vec = np.array([vector]).astype(
            "float32"
        )

        self.index.add(vec)

        self.texts.append(text)

    def search(self, vector, top_k=5):

        vec = np.array([vector]).astype(
            "float32"
        )

        D, I = self.index.search(vec, top_k)

        results = []

        for idx in I[0]:

            if idx < len(self.texts):

                results.append(self.texts[idx])

        return results

    def clear(self):

        self.index = faiss.IndexFlatL2(
            self.index.d
        )
        self.texts = []
