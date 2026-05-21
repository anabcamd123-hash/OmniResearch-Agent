from collections import defaultdict


class Metrics:

    def __init__(self):

        self.total_tokens = 0

        self.llm_calls = 0

        self.tool_calls = 0

        self.retries = 0

        self.tool_usage = defaultdict(int)

    def reset(self):

        self.total_tokens = 0
        self.llm_calls = 0
        self.tool_calls = 0
        self.retries = 0
        self.tool_usage.clear()

    def to_dict(self):

        return {
            "total_tokens": self.total_tokens,
            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,
            "retries": self.retries,
            "tool_usage": dict(self.tool_usage),
        }


metrics = Metrics()
