"""
WorkflowStateManager - 运行态存储

v1.0: Redis 保存运行态
v1.1: SQLite 保存历史态（completed workflow）

状态结构:
{
  "workflow_id": "wf_123",
  "status": "running",
  "tasks": {
    "research": {"status": "completed", "type": "research"},
    "coding_1": {"status": "running", "type": "coding"}
  },
  "created_at": "2026-05-22 09:00:00"
}
"""

import json
import time

from backend.runtime.redis_client import redis_client


class WorkflowStateManager:

    PREFIX = "workflow:state:"

    def save(
        self,
        workflow_id: str,
        state: dict,
    ):
        """保存/更新 workflow 状态"""
        redis_client.set(
            self.PREFIX + workflow_id,
            json.dumps(state),
        )

    def load(self, workflow_id: str) -> dict | None:
        """加载 workflow 状态"""
        data = redis_client.get(
            self.PREFIX + workflow_id
        )
        if not data:
            return None
        return json.loads(data)

    def delete(self, workflow_id: str):
        """删除 workflow 状态"""
        redis_client.delete(
            self.PREFIX + workflow_id
        )

    def list_running(self) -> list[dict]:
        """列出所有 running 状态的 workflow"""
        try:
            keys = redis_client.keys(
                self.PREFIX + "*"
            )
        except Exception:
            return []

        result = []
        for key in keys:
            try:
                data = redis_client.get(key)
                if data:
                    state = json.loads(data)
                    if state.get("status") == "running":
                        result.append(state)
            except Exception:
                continue

        return result

    def update_task_status(
        self,
        workflow_id: str,
        task_id: str,
        status: str,
        task_type: str = None,
    ):
        """
        更新单个 task 的状态

        task_type: 新增，resume 时需要知道类型
        """
        state = self.load(workflow_id)
        if not state:
            return

        state.setdefault("tasks", {})

        # 兼容旧格式 (task_id -> status)
        # 新格式 (task_id -> {status, type})
        existing = state["tasks"].get(task_id)
        if isinstance(existing, dict):
            existing["status"] = status
            if task_type:
                existing["type"] = task_type
        else:
            state["tasks"][task_id] = {
                "status": status,
                "type": task_type or "",
            }

        self.save(workflow_id, state)

    def create_workflow(
        self,
        workflow_id: str,
        task_ids: list[str],
        task_types: dict[str, str] = None,
    ):
        """
        创建新 workflow 初始状态

        task_types: {task_id: task_type} 映射
        """
        task_types = task_types or {}
        state = {
            "workflow_id": workflow_id,
            "status": "running",
            "tasks": {
                tid: {
                    "status": "pending",
                    "type": task_types.get(tid, ""),
                }
                for tid in task_ids
            },
            "created_at": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        self.save(workflow_id, state)

    def mark_completed(self, workflow_id: str):
        """标记 workflow 完成"""
        state = self.load(workflow_id)
        if state:
            state["status"] = "completed"
            self.save(workflow_id, state)

    def mark_failed(self, workflow_id: str):
        """标记 workflow 失败"""
        state = self.load(workflow_id)
        if state:
            state["status"] = "failed"
            self.save(workflow_id, state)

    def get_pending_tasks(
        self, workflow_id: str
    ) -> list[dict]:
        """
        获取 pending 和 running 的 task

        返回: [{"task_id": ..., "task_type": ...}, ...]
        """
        state = self.load(workflow_id)
        if not state:
            return []

        tasks = state.get("tasks", {})
        result = []
        for tid, task_info in tasks.items():
            # 兼容旧格式
            if isinstance(task_info, dict):
                st = task_info["status"]
                tt = task_info.get("type", "")
            else:
                st = task_info
                tt = ""

            if st in ("pending", "running"):
                result.append({
                    "task_id": tid,
                    "task_type": tt,
                })

        return result


workflow_state = WorkflowStateManager()
