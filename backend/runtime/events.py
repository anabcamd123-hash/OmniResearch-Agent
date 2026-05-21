from typing import Callable, Dict, List
from backend.utils.logger import logger


class EventBus:

    def __init__(self):

        self.listeners: Dict[
            str, List[Callable]
        ] = {}

    def subscribe(
        self,
        event_type: str,
        callback: Callable,
    ):

        if event_type not in self.listeners:
            self.listeners[event_type] = []

        self.listeners[event_type].append(
            callback
        )

    async def publish(
        self,
        event_type: str,
        payload: dict,
    ):

        logger.info(
            f"[EventBus] {event_type}: "
            f"{str(payload)[:100]}"
        )

        if event_type not in self.listeners:
            return

        for callback in self.listeners[
            event_type
        ]:
            try:
                if asyncio.iscoroutinefunction(
                    callback
                ):
                    await callback(payload)
                else:
                    callback(payload)
            except Exception as e:
                logger.info(
                    f"[EventBus] Error in "
                    f"{event_type}: {e}"
                )


import asyncio

bus = EventBus()
