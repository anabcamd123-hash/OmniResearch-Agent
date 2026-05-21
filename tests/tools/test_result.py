import pytest
from backend.tools.result import ToolResult


def test_tool_result_success():

    result = ToolResult(
        success=True,
        content="data",
        metadata={"source": "github"},
    )

    assert result.success is True
    assert result.content == "data"
    assert result.metadata["source"] == "github"


def test_tool_result_to_dict():

    result = ToolResult(
        success=False,
        content="error",
    )

    d = result.to_dict()

    assert d["success"] is False
    assert d["content"] == "error"


def test_tool_result_default_metadata():

    result = ToolResult(
        success=True,
        content="ok",
    )

    assert result.metadata == {}
