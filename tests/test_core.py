import pytest
import asyncio
from backend.agents.result import AgentResult
from backend.executor.context import ExecutionContext
from backend.tools.result import ToolResult


def test_agent_result():

    result = AgentResult(
        success=True,
        content="test",
        score=0.9,
    )

    assert result.success is True
    assert result.content == "test"
    assert result.score == 0.9

    d = result.to_dict()
    assert d["success"] is True


def test_tool_result():

    result = ToolResult(
        success=True,
        content="hello",
        metadata={"key": "value"},
    )

    assert result.success is True
    assert result.content == "hello"
    assert result.metadata["key"] == "value"


def test_execution_context():

    ctx = ExecutionContext()

    ctx.set("key1", "value1")
    ctx.set("key2", {"nested": True})

    assert ctx.get("key1") == "value1"
    assert ctx.get("key2") == {"nested": True}
    assert ctx.get("missing", "default") == "default"
    assert ctx.exists("key1") is True
    assert ctx.exists("missing") is False

    dump = ctx.dump()
    assert "key1" in dump

    ctx.clear()
    assert ctx.exists("key1") is False


def test_memory_store():

    from backend.memory.memory_store import MemoryStore

    store = MemoryStore()

    # MemoryStore now uses DB, test basic structure
    assert store.repo is not None


def test_prompt_loader():

    from backend.prompts.loader import load_prompt

    planner = load_prompt("planner")
    assert "workflow planner" in planner

    coding = load_prompt("coding")
    assert "Python code" in coding


def test_metrics():

    from backend.runtime.metrics import Metrics

    m = Metrics()
    m.total_tokens = 100
    m.llm_calls = 5
    m.tool_usage["github"] = 3

    d = m.to_dict()
    assert d["total_tokens"] == 100
    assert d["llm_calls"] == 5
    assert d["tool_usage"]["github"] == 3


def test_trace_store():

    from backend.runtime.trace_store import TraceStore

    store = TraceStore()
    store.add("test_event", {"key": "value"})

    recent = store.recent(10)
    assert len(recent) == 1
    assert recent[0]["event"] == "test_event"


def test_agent_stats():

    from backend.runtime.agent_stats import AgentStats

    stats = AgentStats()
    stats.record("research", 2.5)
    stats.record("research", 3.0)

    d = stats.to_dict()
    assert d["research"]["calls"] == 2
    assert d["research"]["avg_duration"] == 2.75
