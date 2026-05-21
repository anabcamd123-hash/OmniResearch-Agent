from collections import defaultdict


class AgentStats:

    def __init__(self):

        self.calls = defaultdict(int)

        self.total_duration = defaultdict(float)

    def record(
        self,
        agent: str,
        duration: float,
    ):

        self.calls[agent] += 1

        self.total_duration[agent] += duration

    def to_dict(self):

        result = {}

        for agent in self.calls:

            avg = (
                self.total_duration[agent]
                / self.calls[agent]
                if self.calls[agent] > 0
                else 0
            )

            result[agent] = {
                "calls": self.calls[agent],
                "total_duration": round(
                    self.total_duration[agent], 2
                ),
                "avg_duration": round(avg, 2),
            }

        return result


agent_stats = AgentStats()
