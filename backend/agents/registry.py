"""
Agent Registry - 工厂模式

不共享实例，保证并发安全。
新增 Agent 只需注册一行。
"""

from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent

# 未来可以加 AutoFixAgent
# from backend.agents.autofix_agent import AutoFixAgent

AGENT_REGISTRY = {
    "research": ResearchAgent,
    "coding": CodingAgent,
    "verify": VerifyAgent,
    "reflection": ReflectionAgent,
    # "autofix": AutoFixAgent,
}


def get_agent(agent_type: str):
    """返回 agent 实例"""
    agent_cls = AGENT_REGISTRY.get(agent_type)
    if not agent_cls:
        raise ValueError(
            f"Unknown agent type: {agent_type}"
        )
    return agent_cls()
