from datetime import datetime


class MemoryStore:

    def __init__(self):

        self.memories = []

    def add(self, item):

        record = {
            "data": item,
            "time": datetime.now().strftime(
                "%H:%M:%S"
            )
        }

        self.memories.append(record)

    def get_recent(
        self,
        limit=10
    ):

        return [
            m["data"]
            for m in self.memories[-limit:]
        ]

    def clear(self):

        self.memories = []


memory = MemoryStore()
