from collections import deque
from datetime import datetime


class TraceStore:

    def __init__(self):

        self.events = deque(maxlen=5000)

    def add(
        self,
        event_type: str,
        payload: dict,
    ):

        self.events.append({
            "time": datetime.utcnow().isoformat(),
            "event": event_type,
            "payload": payload,
        })

    def recent(
        self,
        limit=100,
    ):

        return list(self.events)[-limit:]


trace_store = TraceStore()
