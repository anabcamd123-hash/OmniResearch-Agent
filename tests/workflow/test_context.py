import pytest
from backend.executor.context import ExecutionContext


def test_context_set_get():

    ctx = ExecutionContext()

    ctx.set("key", "value")

    assert ctx.get("key") == "value"


def test_context_default():

    ctx = ExecutionContext()

    assert ctx.get("missing", "default") == "default"


def test_context_exists():

    ctx = ExecutionContext()

    ctx.set("exists", True)

    assert ctx.exists("exists") is True
    assert ctx.exists("nope") is False


def test_context_dump():

    ctx = ExecutionContext()

    ctx.set("a", 1)
    ctx.set("b", 2)

    dump = ctx.dump()

    assert dump == {"a": 1, "b": 2}


def test_context_clear():

    ctx = ExecutionContext()

    ctx.set("key", "value")
    ctx.clear()

    assert ctx.exists("key") is False
