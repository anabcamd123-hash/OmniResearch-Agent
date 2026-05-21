from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentResult:

    success: bool
    content: Any
    score: float = 1.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "success": self.success,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
        }
