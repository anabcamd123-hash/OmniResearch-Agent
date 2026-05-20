import logging
import asyncio

from backend.api.ws_manager import manager

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s'
)

logger = logging.getLogger("omniresearch")

async def stream_log(message: str):

    logger.info(message)

    try:
        await manager.broadcast(message)

    except:
        pass
token_usage = {"total": 0}

def log_tokens(tokens: int):
    token_usage["total"] += tokens
