"""
统一工具返回值

所有 Tool 必须返回 ToolResult
异常由 Sandbox 捕获，不传播到 Agent
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:

    success: bool
    content: Any = None
    error: str | None = None
    metadata: dict = field(
        default_factory=dict
    )

    def to_dict(self):
        return {
            "success": self.success,
            "content": self.content,
            "error": self.error,
            "metadata": self.metadata,
        }
