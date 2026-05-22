"""
VerifyResult - 验证结果（结构化 JSON 输出）

替代旧的字符串解析：
  ❌ re.search(r"score[:\s]*(\d+)", ...)
  ✓ json.loads(response)
"""

from dataclasses import dataclass, field


@dataclass
class VerifyResult:

    passed: bool
    score: float
    issues: list[str] = field(
        default_factory=list
    )
    feedback: str = ""
