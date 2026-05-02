import logging
from typing import Generator, Optional

from src.iterator import TaskQueueIterator, AsyncTaskQueueIterator
from src.models import Priority, Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self) -> None:
        self._tasks: list[Task] = []
        logger.info("TaskQueue created")

    def enqueue(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError(f"Expected Task, got {type(task).__name__!r}")
        self._tasks.append(task)
        logger.info("Task enqueued: id=%s", task.id)

    def dequeue(self) -> Task:
        if not self._tasks:
            raise IndexError("dequeue from an empty TaskQueue")
        task = self._tasks.pop(0)
        logger.info("Task dequeued: id=%s", task.id)
        return task

    def __iter__(self) -> TaskQueueIterator:
        return TaskQueueIterator(self._tasks)
    
    def __aiter__(self):
        return AsyncTaskQueueIterator(self._tasks)
    
    def __len__(self) -> int:
        return len(self._tasks)

    def __repr__(self) -> str:
        return f"TaskQueue({len(self._tasks)} tasks)"

    def filter_by_status(self, status: TaskStatus) -> Generator[Task, None, None]:
        for task in self._tasks:
            if task.status == status:
                yield task
    
    async def afilter_by_status(self, status: TaskStatus):
        async for task in self:
            if task.status == status:
                yield task

    def filter_by_priority(self, priority: Priority) -> Generator[Task, None, None]:
        for task in self._tasks:
            if task.priority == priority:
                yield task

    async def afilter_by_priority(self, priority: Priority):
        async for task in self:
            if task.priority == priority:
                yield task

    def filter_by(
        self,
        *,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
    ) -> Generator[Task, None, None]:
        for task in self._tasks:
            if status is not None and task.status != status:
                continue
            if priority is not None and task.priority != priority:
                continue
            yield task

    async def afilter_by(
        self,
        *,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
    ):
        async for task in self:
            if status is not None and task.status != status:
                continue
            if priority is not None and task.priority != priority:
                continue
            yield task