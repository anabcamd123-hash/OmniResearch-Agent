"""
Test: TaskGraph 依赖解析
"""

import pytest
from backend.executor.task_graph import TaskGraph
from backend.executor.task import Task


def test_task_graph_basic():
    graph = TaskGraph()
    graph.add_task(
        Task(task_id="a", task_type="research", dependencies=[])
    )
    graph.add_task(
        Task(task_id="b", task_type="coding", dependencies=["a"])
    )

    # a 没有依赖，应该 ready
    ready = graph.get_ready_tasks(set())
    assert len(ready) == 1
    assert ready[0].task_id == "a"

    # a 完成后 b ready
    ready = graph.get_ready_tasks({"a"})
    assert len(ready) == 1
    assert ready[0].task_id == "b"

    # 全部完成，没有 ready
    ready = graph.get_ready_tasks({"a", "b"})
    assert len(ready) == 0


def test_task_graph_parallel():
    graph = TaskGraph()
    graph.add_task(
        Task(task_id="r1", task_type="research", dependencies=[])
    )
    graph.add_task(
        Task(task_id="r2", task_type="research", dependencies=[])
    )
    graph.add_task(
        Task(task_id="c1", task_type="coding", dependencies=["r1", "r2"])
    )

    # r1, r2 都 ready
    ready = graph.get_ready_tasks(set())
    ids = {t.task_id for t in ready}
    assert ids == {"r1", "r2"}

    # 只完成 r1，c1 还不能跑
    ready = graph.get_ready_tasks({"r1"})
    ids = {t.task_id for t in ready}
    assert ids == {"r2"}
    assert "c1" not in ids

    # r1, r2 都完成，c1 ready
    ready = graph.get_ready_tasks({"r1", "r2"})
    assert len(ready) == 1
    assert ready[0].task_id == "c1"


def test_task_graph_total():
    graph = TaskGraph()
    graph.add_task(Task(task_id="a", task_type="research"))
    graph.add_task(Task(task_id="b", task_type="coding"))
    assert graph.total() == 2
