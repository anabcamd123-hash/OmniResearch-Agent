from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent


class AgentRegistry:

    def __init__(self):

        self.agents = {
            "research": ResearchAgent(),
            "coding": CodingAgent(),
            "verify": VerifyAgent(),
            "reflection": ReflectionAgent(),
        }

    def get(self, agent_type: str):

        if agent_type not in self.agents:
            raise ValueError(
                f"Unknown agent: {agent_type}"
            )

        return self.agents[agent_type]


registry = AgentRegistry()
