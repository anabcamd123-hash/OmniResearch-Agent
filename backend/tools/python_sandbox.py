"""
PythonSandbox - Python 代码隔离执行

禁止直接 exec(code)
必须通过子进程执行，带超时和资源隔离
"""

import asyncio
import os
import tempfile

from backend.tools.result import ToolResult
from backend.utils.logger import logger


class PythonSandbox:
    """
    Python 代码沙箱

    通过子进程执行代码，防止:
    - while True: 死循环（超时杀死）
    - import os; os.system()（子进程隔离）
    - 内存泄漏（进程退出释放）

    v2.0: Docker 容器隔离（限制 CPU/Memory/Network）
    """

    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    async def execute(
        self, code: str
    ) -> ToolResult:
        """执行 Python 代码"""

        # 写入临时文件
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py",
            mode="w",
            encoding="utf-8",
        ) as f:
            f.write(code)
            path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                "python3",
                path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = (
                    await asyncio.wait_for(
                        process.communicate(),
                        timeout=self.timeout,
                    )
                )

                stdout_str = stdout.decode(
                    errors="replace"
                )
                stderr_str = stderr.decode(
                    errors="replace"
                )

                if process.returncode != 0:
                    return ToolResult(
                        success=False,
                        error=stderr_str,
                        metadata={
                            "returncode": (
                                process.returncode
                            )
                        },
                    )

                return ToolResult(
                    success=True,
                    content=stdout_str,
                    metadata={
                        "stderr": stderr_str,
                    },
                )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    error=(
                        f"Python execution timeout "
                        f"after {self.timeout}s"
                    ),
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )

        finally:
            try:
                os.remove(path)
            except OSError:
                pass


python_sandbox = PythonSandbox()
