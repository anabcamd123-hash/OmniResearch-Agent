from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:

    event_type: str

    payload: dict

    timestamp: str = (
        datetime.utcnow().isoformat()
    )
