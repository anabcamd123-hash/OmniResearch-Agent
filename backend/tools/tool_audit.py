"""
ToolAudit - 工具审计日志

记录每次工具调用的成功率、延迟，
供 Dashboard 展示
"""

import time
from collections import defaultdict


class ToolAudit:

    def __init__(self):
        self.records: list[dict] = []
        self.stats: dict[str, dict] = defaultdict(
            lambda: {
                "total": 0,
                "success": 0,
                "fail": 0,
                "total_duration": 0.0,
            }
        )

    def add(
        self,
        tool: str,
        success: bool,
        duration: float,
        error: str | None = None,
    ):
        """记录一次工具调用"""
        record = {
            "tool": tool,
            "success": success,
            "duration": round(duration, 3),
            "error": error,
            "time": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        self.records.append(record)

        # 更新统计
        s = self.stats[tool]
        s["total"] += 1
        if success:
            s["success"] += 1
        else:
            s["fail"] += 1
        s["total_duration"] += duration

        # 控制内存：保留最近500条
        if len(self.records) > 500:
            self.records = self.records[-500:]

    def get_stats(self) -> dict:
        """返回所有工具的统计"""
        result = {}
        for tool, s in self.stats.items():
            total = s["total"]
            avg = (
                s["total_duration"] / total
                if total > 0
                else 0
            )
            result[tool] = {
                "total": total,
                "success": s["success"],
                "fail": s["fail"],
                "success_rate": (
                    round(
                        s["success"] / total * 100,
                        1,
                    )
                    if total > 0
                    else 0
                ),
                "avg_latency": round(avg, 3),
            }
        return result

    def get_recent(
        self, limit: int = 50
    ) -> list[dict]:
        """返回最近的调用记录"""
        return self.records[-limit:]


tool_audit = ToolAudit()
