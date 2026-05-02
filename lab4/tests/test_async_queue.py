"""Тесты асинхронной итерации TaskQueue."""
import pytest
from src.models import Priority, Task, TaskStatus
from src.queue import TaskQueue
from src.iterator import AsyncTaskQueueIterator


def make_task(tid: str, status: TaskStatus = TaskStatus.PENDING) -> Task:
    return Task(tid, f"payload-{tid}", status, Priority.MEDIUM)


# ---------- AsyncTaskQueueIterator ----------

@pytest.mark.asyncio
async def test_async_iterator_yields_all():
    tasks = [make_task("a"), make_task("b"), make_task("c")]
    q = TaskQueue()
    for t in tasks:
        q.enqueue(t)

    result = []
    async for task in q:
        result.append(task.id)

    assert result == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_async_iterator_empty_queue():
    q = TaskQueue()
    result = [t async for t in q]
    assert result == []


@pytest.mark.asyncio
async def test_async_iterator_independent_from_sync():
    """Синхронный и асинхронный итераторы работают независимо."""
    q = TaskQueue()
    q.enqueue(make_task("x"))
    q.enqueue(make_task("y"))

    sync_ids  = [t.id for t in q]
    async_ids = [t.id async for t in q]

    assert sync_ids == async_ids


@pytest.mark.asyncio
async def test_async_iterator_multiple_passes():
    """Повторный async for создаёт новый итератор."""
    q = TaskQueue()
    q.enqueue(make_task("p"))
    q.enqueue(make_task("q"))

    first  = [t.id async for t in q]
    second = [t.id async for t in q]
    assert first == second


# ---------- afilter_by_status ----------

@pytest.mark.asyncio
async def test_afilter_by_status_pending():
    q = TaskQueue()
    q.enqueue(make_task("p1", TaskStatus.PENDING))
    q.enqueue(make_task("d1", TaskStatus.DONE))
    q.enqueue(make_task("p2", TaskStatus.PENDING))

    result = [t.id async for t in q.afilter_by_status(TaskStatus.PENDING)]
    assert result == ["p1", "p2"]


@pytest.mark.asyncio
async def test_afilter_by_status_empty_result():
    q = TaskQueue()
    q.enqueue(make_task("d1", TaskStatus.DONE))

    result = [t async for t in q.afilter_by_status(TaskStatus.PENDING)]
    assert result == []


# ---------- afilter_by_priority ----------

@pytest.mark.asyncio
async def test_afilter_by_priority():
    q = TaskQueue()
    q.enqueue(Task("h", "p", TaskStatus.PENDING, Priority.HIGH))
    q.enqueue(Task("m", "p", TaskStatus.PENDING, Priority.MEDIUM))
    q.enqueue(Task("l", "p", TaskStatus.PENDING, Priority.LOW))

    result = [t.id async for t in q.afilter_by_priority(Priority.HIGH)]
    assert result == ["h"]


# ---------- afilter_by (combined) ----------

@pytest.mark.asyncio
async def test_afilter_by_combined():
    q = TaskQueue()
    q.enqueue(Task("a", "p", TaskStatus.PENDING, Priority.HIGH))
    q.enqueue(Task("b", "p", TaskStatus.DONE,    Priority.HIGH))
    q.enqueue(Task("c", "p", TaskStatus.PENDING, Priority.LOW))

    result = [
        t.id async for t in q.afilter_by(status=TaskStatus.PENDING, priority=Priority.HIGH)
    ]
    assert result == ["a"]
