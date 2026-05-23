_model = None


def _load_model():
    """延迟加载模型，仅在首次使用时导入和加载"""
    global _model
    if _model is None:
        from sentence_transformers import (
            SentenceTransformer,
        )
        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )
    return _model


class Embedder:

    def __init__(self):
        # 不在初始化时导入或加载
        pass

    def encode(self, text: str):
        model = _load_model()
        return model.encode(text).tolist()
