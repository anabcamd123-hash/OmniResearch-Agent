from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:

    success: bool

    content: Any

    metadata: dict = field(
        default_factory=dict
    )

    def to_dict(self):

        return {
            "success": self.success,
            "content": self.content,
            "metadata": self.metadata,
        }
