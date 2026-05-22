"""
Test: DAGExecutor 执行逻辑（集成测试用 mock）
"""

import pytest
import asyncio
from backend.executor.dag_executor import DAGExecutor
from backend.executor.task import Task
from backend.runtime.runtime_state import state


@pytest.mark.asyncio
async def test_dag_executor_basic():
    """基本执行流程（需 mock agent）"""
    from unittest.mock import patch, AsyncMock

    mock_agent = AsyncMock()
    mock_agent.run = AsyncMock(return_value="ok")

    with patch(
        "backend.executor.dag_executor.get_agent",
        return_value=mock_agent,
    ):
        executor = DAGExecutor()
        tasks = [
            Task(task_id="a", task_type="research", dependencies=[]),
            Task(task_id="b", task_type="coding", dependencies=["a"]),
        ]
        await executor.execute(tasks)

        assert "a" in executor.completed_tasks
        assert "b" in executor.completed_tasks
        assert tasks[0].status == "completed"
        assert tasks[1].status == "completed"


@pytest.mark.asyncio
async def test_dag_executor_failure():
    """任务失败 → DLQ"""
    from unittest.mock import patch, AsyncMock

    mock_agent = AsyncMock()
    mock_agent.run = AsyncMock(side_effect=RuntimeError("boom"))

    with patch(
        "backend.executor.dag_executor.get_agent",
        return_value=mock_agent,
    ):
        with patch(
            "backend.executor.dag_executor.dlq_push",
            new_callable=AsyncMock,
        ) as mock_dlq:
            executor = DAGExecutor()
            tasks = [
                Task(task_id="fail", task_type="research", dependencies=[]),
            ]
            await executor.execute(tasks)

            assert "fail" in executor.completed_tasks
            assert tasks[0].status == "failed"
            mock_dlq.assert_called()
