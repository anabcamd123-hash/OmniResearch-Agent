"""
ReflectionResult - 反射结果（结构化 JSON 输出）

替代旧的字符串判断：
  ❌ "true" in output.lower()
  ✓ json.loads(response)
"""

from dataclasses import dataclass


@dataclass
class ReflectionResult:

    need_retry: bool
    root_cause: str = ""
    suggestion: str = ""
