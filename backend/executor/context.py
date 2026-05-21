from typing import Any


class ExecutionContext:

    def __init__(self):

        self.data = {}

    def set(
        self,
        key: str,
        value: Any,
    ):

        self.data[key] = value

    def get(
        self,
        key: str,
        default=None,
    ):

        return self.data.get(
            key,
            default,
        )

    def exists(
        self,
        key: str,
    ):

        return key in self.data

    def dump(self):

        return self.data

    def clear(self):

        self.data = {}
