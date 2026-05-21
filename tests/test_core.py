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
    assert store.repo is not None


def test_prompt_loader():

    from backend.prompts.loader import load_prompt

    planner = load_prompt("planner")
    assert "workflow planner" in planner

    coding = load_prompt("coding")
    assert "Python code" in coding

    verify = load_prompt("verify")
    assert "Score" in verify

    reflection = load_prompt("reflection")
    assert "reflection system" in reflection


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


def test_event_bus():

    from collections import defaultdict

    class TestEventBus:
        def __init__(self):
            self.subscribers = defaultdict(list)

        def subscribe(self, event_type, callback):
            self.subscribers[event_type].append(callback)

        async def publish(self, event_type, payload):
            for cb in self.subscribers.get(event_type, []):
                await cb(payload)

    bus = TestEventBus()
    results = []

    async def handler(payload):
        results.append(payload)

    bus.subscribe("test_event", handler)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        bus.publish("test_event", {"data": "hello"})
    )
    loop.close()

    assert len(results) == 1
    assert results[0]["data"] == "hello"


def test_mcp_registry():

    from backend.mcp.models import MCPTool
    from backend.mcp.registry import MCPRegistry

    registry = MCPRegistry()

    tool = MCPTool(
        name="test_tool",
        description="A test tool",
        server="http://localhost:9001",
    )

    registry.register(tool)

    assert registry.get("test_tool") == tool
    assert registry.get("missing") is None
    assert len(registry.all()) == 1


def test_config_settings():

    from backend.config.settings import settings

    assert settings.MODEL_PROVIDER in [
        "openai", "gemini", "deepseek", "ollama"
    ]
    assert settings.RAG_TOP_K > 0
    assert settings.DATABASE_URL is not None
