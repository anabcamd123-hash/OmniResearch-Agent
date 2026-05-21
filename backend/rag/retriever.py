from backend.rag.embeddings import embed


class Retriever:

    def __init__(self, store):

        self.store = store

    def retrieve(
        self,
        query,
        k=3
    ):

        q = embed([query])[0]

        return self.store.search(q, k)
