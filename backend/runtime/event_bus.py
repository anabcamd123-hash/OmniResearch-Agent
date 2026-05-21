import asyncio
from collections import defaultdict
from backend.utils.logger import logger


class EventBus:

    def __init__(self):

        self.subscribers = defaultdict(list)

    def subscribe(
        self,
        event_type: str,
        callback,
    ):

        self.subscribers[event_type].append(
            callback
        )

    async def publish(
        self,
        event_type: str,
        payload: dict,
    ):

        # Inject event type for trace
        payload["_event_type"] = event_type

        callbacks = self.subscribers.get(
            event_type,
            [],
        )

        if not callbacks:
            return

        await asyncio.gather(
            *[
                callback(payload)
                for callback in callbacks
            ],
            return_exceptions=True,
        )


event_bus = EventBus()
