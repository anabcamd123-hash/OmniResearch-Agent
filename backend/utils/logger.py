import logging
from backend.api.ws_manager import manager
from backend.storage.repository import TokenRepository

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s'
)

logger = logging.getLogger('omniresearch')

token_repo = TokenRepository()


def log_tokens(tokens: int):
    # Write to SQLite (single source)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(
                token_repo.record_usage(
                    task_id="system",
                    agent="unknown",
                    prompt_tokens=0,
                    completion_tokens=tokens,
                    total_tokens=tokens,
                )
            )
    except Exception:
        pass


async def stream_log(message: str):
    logger.info(message)
    try:
        await manager.broadcast(message)
    except Exception:
        pass
