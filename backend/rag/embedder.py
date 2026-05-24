import logging
import os

logger = logging.getLogger(__name__)

_model = None
_load_failed = False


def _load_model():
    """延迟加载模型，仅在首次使用时导入和加载"""
    global _model, _load_failed
    if _load_failed:
        return None
    if _model is None:
        try:
            # 设置较短的超时，避免长时间阻塞
            os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
            from sentence_transformers import (
                SentenceTransformer,
            )
            _model = SentenceTransformer(
                "all-MiniLM-L6-v2",
            )
        except Exception as e:
            logger.warning(
                f"[Embedder] Model load failed: "
                f"{e}. RAG disabled."
            )
            _load_failed = True
            return None
    return _model


class Embedder:

    def __init__(self):
        # 不在初始化时导入或加载
        pass

    def encode(self, text: str):
        model = _load_model()
        if model is None:
            # 返回空向量，保持 dim=384
            return [0.0] * 384
        return model.encode(text).tolist()
