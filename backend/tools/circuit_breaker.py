"""
Layer 2: Circuit Breaker（熔断器）
保护下游服务，防止级联失败
"""

import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"       # 正常，允许调用
    OPEN = "open"           # 熔断，拒绝调用
    HALF_OPEN = "half_open" # 试探恢复


class CircuitBreaker:
    """
    熔断器

    状态机:
        CLOSED --[连续失败>=阈值]--> OPEN
        OPEN --[经过recovery_time]--> HALF_OPEN
        HALF_OPEN --[成功]--> CLOSED
        HALF_OPEN --[失败]--> OPEN

    v1.0: 进程内状态，不持久化
    v2.0: Redis共享状态（多Worker场景）
    """

    def __init__(
        self,
        threshold: int = 5,
        recovery_time: int = 60,
    ):
        self.threshold = threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure: float | None = None
        self.state = CircuitState.CLOSED

    def allow(self) -> bool:
        """判断是否允许调用"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure is None:
                self.state = CircuitState.CLOSED
                return True

            elapsed = time.time() - self.last_failure
            if elapsed >= self.recovery_time:
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # HALF_OPEN: 允许一次试探
        return True

    def success(self):
        """调用成功，重置状态"""
        self.failures = 0
        self.state = CircuitState.CLOSED

    def fail(self):
        """调用失败，累加计数"""
        self.failures += 1
        self.last_failure = time.time()

        if self.failures >= self.threshold:
            self.state = CircuitState.OPEN

    @property
    def status(self) -> dict:
        """返回当前状态（监控用）"""
        return {
            "state": self.state.value,
            "failures": self.failures,
            "threshold": self.threshold,
            "recovery_time": self.recovery_time,
            "last_failure": self.last_failure,
        }
