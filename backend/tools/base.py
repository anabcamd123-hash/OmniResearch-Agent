"""
BaseTool - 工具基类

所有工具必须:
1. 继承 BaseTool
2. 实现 async run() 返回 ToolResult（或任何值，由 Sandbox 包装）
3. 禁止直接实例调用，必须通过 ToolRouter → Sandbox
"""

from abc import ABC, abstractmethod
from backend.tools.result import ToolResult


class BaseTool(ABC):

    name: str
    description: str

    @abstractmethod
    async def run(self, input: str):
        """
        执行工具

        可以返回:
        - ToolResult（推荐）
        - 任何值（Sandbox 会包装为 ToolResult）
        - 抛异常（Sandbox 会捕获为 ToolResult）

        注意: 超时由 Sandbox 控制，不需要在工具内处理
        """
        pass
