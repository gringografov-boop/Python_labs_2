import pytest
from src.models import Task, TaskStatus, Priority
from src.queue import TaskQueue


@pytest.fixture
def sample_tasks() -> list[Task]:
    return [
        Task("t1", "payload-1", TaskStatus.PENDING, Priority.LOW),
        Task("t2", "payload-2", TaskStatus.PENDING, Priority.HIGH),
        Task("t3", "payload-3", TaskStatus.DONE, Priority.MEDIUM),
        Task("t4", "payload-4", TaskStatus.FAILED, Priority.HIGH),
        Task("t5", "payload-5", TaskStatus.PENDING, Priority.MEDIUM),
    ]


@pytest.fixture
def queue(sample_tasks) -> TaskQueue:
    q = TaskQueue()
    for t in sample_tasks:
        q.enqueue(t)
    return q
