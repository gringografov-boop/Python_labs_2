import pytest

from src.handler import TaskHandler
from src.executors import LoggingExecutor, EmailExecutor, DatabaseExecutor
from src.models import Task, TaskStatus, Priority
from src.queue import TaskQueue


def make_task(task_id: str = "t1", status: TaskStatus = TaskStatus.PENDING) -> Task:
    return Task(task_id, f"payload-{task_id}", status, Priority.MEDIUM)


def make_queue(*task_ids: str) -> TaskQueue:
    q = TaskQueue()
    for tid in task_ids:
        q.enqueue(make_task(tid))
    return q


@pytest.mark.asyncio
async def test_handle_task_sets_done():
    handler = TaskHandler([LoggingExecutor()])
    task = make_task()
    await handler.handle_task(task)
    assert task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_handle_task_multiple_executors():
    handler = TaskHandler([LoggingExecutor(), EmailExecutor(), DatabaseExecutor()])
    task = make_task()
    await handler.handle_task(task)
    assert task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_handle_task_failing_executor_sets_failed():
    class AlwaysFailExecutor:
        name = "AlwaysFail"
        async def execute(self, task: Task) -> None:
            raise RuntimeError("deliberate failure")

    handler = TaskHandler([AlwaysFailExecutor()])
    task = make_task()
    await handler.handle_task(task)
    assert task.status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_handle_all_only_pending():
    q = TaskQueue()
    pending = make_task("p1", TaskStatus.PENDING)
    done    = make_task("d1", TaskStatus.DONE)
    q.enqueue(pending)
    q.enqueue(done)

    handler = TaskHandler([LoggingExecutor()])
    await handler.handle_all(q)

    assert pending.status == TaskStatus.DONE
    assert done.status == TaskStatus.DONE   # не изменился


@pytest.mark.asyncio
async def test_handle_all_empty_queue():
    handler = TaskHandler([LoggingExecutor()])
    q = TaskQueue()
    await handler.handle_all(q)   # не должно падать


@pytest.mark.asyncio
async def test_handle_concurrent_all_done():
    q = make_queue("c1", "c2", "c3")
    handler = TaskHandler([LoggingExecutor()])
    await handler.handle_concurrent(q)
    for task in q:
        assert task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_handle_concurrent_skips_non_pending():
    q = TaskQueue()
    q.enqueue(make_task("x1", TaskStatus.PENDING))
    q.enqueue(make_task("x2", TaskStatus.DONE))
    handler = TaskHandler([LoggingExecutor()])
    await handler.handle_concurrent(q)
    tasks = list(q)
    assert tasks[0].status == TaskStatus.DONE
    assert tasks[1].status == TaskStatus.DONE   # не изменился


@pytest.mark.asyncio
async def test_handler_no_executors():
    handler = TaskHandler([])
    task = make_task()
    await handler.handle_task(task)
    assert task.status == TaskStatus.DONE
