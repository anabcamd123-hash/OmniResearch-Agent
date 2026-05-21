import pytest
from backend.agents.result import AgentResult


def test_agent_result_creation():

    result = AgentResult(
        success=True,
        content="test output",
        score=0.95,
    )

    assert result.success is True
    assert result.content == "test output"
    assert result.score == 0.95


def test_agent_result_to_dict():

    result = AgentResult(
        success=False,
        content="error",
        score=0.0,
        metadata={"retry": 3},
    )

    d = result.to_dict()

    assert d["success"] is False
    assert d["content"] == "error"
    assert d["metadata"]["retry"] == 3


def test_agent_result_default_metadata():

    result = AgentResult(
        success=True,
        content="ok",
    )

    assert result.metadata == {}
