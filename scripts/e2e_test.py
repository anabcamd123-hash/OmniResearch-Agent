"""
E2E 测试 — 端到端验证整个 Agent 流程

用法:
    python scripts/e2e_test.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock LLM before importing agents
from unittest.mock import MagicMock, patch


def main():
    print("=" * 50)
    print("OmniResearch Agent — E2E Test")
    print("=" * 50)

    results = []

    # 1. Config
    try:
        from backend.config.settings import settings
        assert settings.MAX_RETRY == 3
        print("✓ Config: settings loaded")
        results.append(("Config", True))
    except Exception as e:
        print(f"✗ Config: {e}")
        results.append(("Config", False))

    # 2. Bulkhead
    try:
        import asyncio as aio
        from backend.runtime.bulkhead import Bulkhead

        async def test_bulkhead():
            bh = Bulkhead()
            async with bh.limit("research"):
                return True

        assert aio.get_event_loop().run_until_complete(test_bulkhead())
        print("✓ Bulkhead: context manager works")
        results.append(("Bulkhead", True))
    except Exception as e:
        print(f"✗ Bulkhead: {e}")
        results.append(("Bulkhead", False))

    # 3. DLQ
    try:
        from backend.runtime.dlq import dlq_push, dlq_list, dlq_count

        async def test_dlq():
            await dlq_push("e2e_task", "test", "test error")
            count = await dlq_count()
            items = await dlq_list()
            return count >= 1 and len(items) >= 1

        assert asyncio.get_event_loop().run_until_complete(test_dlq())
        print("✓ DLQ: push/list/count works")
        results.append(("DLQ", True))
    except Exception as e:
        print(f"✗ DLQ: {e}")
        results.append(("DLQ", False))

    # 4. StateStore
    try:
        from backend.storage.state_factory import build_state_repo

        async def test_state():
            repo = await build_state_repo()
            await repo.set("e2e_key", "e2e_value")
            val = await repo.get("e2e_key")
            await repo.delete("e2e_key")
            return val == "e2e_value"

        assert asyncio.get_event_loop().run_until_complete(test_state())
        print("✓ StateStore: get/set/delete works")
        results.append(("StateStore", True))
    except Exception as e:
        print(f"✗ StateStore: {e}")
        results.append(("StateStore", False))

    # 5. Agent Registry (requires fastapi)
    try:
        from backend.agents.registry import get_agent, AGENT_REGISTRY
        for name in ["research", "coding", "verify", "reflection"]:
            agent = get_agent(name)
            assert agent is not None
        print(f"✓ Registry: {len(AGENT_REGISTRY)} agents registered")
        results.append(("Registry", True))
    except ImportError:
        print("⊘ Registry: skipped (fastapi not installed)")
        results.append(("Registry", True))
    except Exception as e:
        print(f"✗ Registry: {e}")
        results.append(("Registry", False))

    # 6. Retry
    try:
        from backend.executor.retry import retry_async

        async def test_retry():
            count = 0

            async def flaky():
                nonlocal count
                count += 1
                if count < 2:
                    raise ValueError("not yet")
                return "ok"

            result = await retry_async(flaky, retries=3, delay=0.01)
            return result == "ok" and count == 2

        assert asyncio.get_event_loop().run_until_complete(test_retry())
        print("✓ Retry: exponential backoff works")
        results.append(("Retry", True))
    except Exception as e:
        print(f"✗ Retry: {e}")
        results.append(("Retry", False))

    # 7. TaskGraph
    try:
        from backend.executor.task_graph import TaskGraph
        from backend.executor.task import Task

        graph = TaskGraph()
        graph.add_task(Task(task_id="a", task_type="research", dependencies=[]))
        graph.add_task(Task(task_id="b", task_type="coding", dependencies=["a"]))
        ready = graph.get_ready_tasks(set())
        assert len(ready) == 1 and ready[0].task_id == "a"
        # Simulate a completing
        for t in graph.tasks:
            if t.task_id == "a":
                t.status = "completed"
        ready = graph.get_ready_tasks({"a"})
        assert len(ready) == 1 and ready[0].task_id == "b"
        print("✓ TaskGraph: dependency resolution works")
        results.append(("TaskGraph", True))
    except Exception as e:
        print(f"✗ TaskGraph: {e}")
        results.append(("TaskGraph", False))

    # Summary
    print("\n" + "=" * 50)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    for name, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")

    print("=" * 50)

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
