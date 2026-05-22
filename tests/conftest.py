"""
Test fixtures — Mock LLM + 公共配置
"""

import pytest


class MockLLM:
    """模拟 LLM，返回固定结果"""

    def __init__(self, response: str = None):
        self.response = response or (
            '{"tasks": ['
            '{"id": "research_1", '
            '"type": "research", '
            '"depends": []}, '
            '{"id": "coding_1", '
            '"type": "coding", '
            '"depends": ["research_1"]}, '
            '{"id": "verify_1", '
            '"type": "verify", '
            '"depends": ["coding_1"]}, '
            '{"id": "reflection_1", '
            '"type": "reflection", '
            '"depends": ["verify_1"]}'
            ']}'
        )

    def invoke(self, prompt, temperature=0.2):
        return self.response


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    """全局 Mock LLM，避免真实 API 调用"""
    monkeypatch.setattr(
        "backend.llm.provider_factory.get_provider",
        lambda: MockLLM(),
    )
