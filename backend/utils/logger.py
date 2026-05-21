import logging
from backend.api.ws_manager import manager
from backend.runtime.metrics import metrics

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s'
)

logger = logging.getLogger('omniresearch')


def log_tokens(tokens: int):

    metrics.total_tokens += tokens
    metrics.llm_calls += 1
