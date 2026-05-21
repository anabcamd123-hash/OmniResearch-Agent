from sentence_transformers import (
    SentenceTransformer,
)

_model = None


class Embedder:

    def __init__(self):

        global _model
        if _model is None:
            _model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        self.model = _model

    def encode(self, text: str):

        return self.model.encode(text).tolist()
