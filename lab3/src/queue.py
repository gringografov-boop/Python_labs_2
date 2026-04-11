import logging
from typing import Generator, Optional

from src.iterator import TaskQueueIterator
from src.models import Priority, Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self) -> None:
        self._tasks: list[Task] = []
        logger.info("TaskQueue created")

    def enqueue(self, task: Task) -> None:
        if not isinstance(task, Task):
            logger.error("enqueue failed: expected Task, got %s", type(task).__name__)
            raise TypeError(f"Expected Task, got {type(task).__name__!r}")

        self._tasks.append(task)
        logger.info(
            "Task enqueued: id=%s status=%s priority=%s",
            task.id,
            task.status.name,
            task.priority.name,
        )

    def dequeue(self) -> Task:
        if not self._tasks:
            logger.error("dequeue failed: queue is empty")
            raise IndexError("dequeue from an empty TaskQueue")

        task = self._tasks.pop(0)
        logger.info("Task dequeued: id=%s", task.id)
        return task

    def __iter__(self) -> TaskQueueIterator:
        logger.info("Iterator requested for queue with %d tasks", len(self._tasks))
        return TaskQueueIterator(self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __repr__(self) -> str:
        return f"TaskQueue({len(self._tasks)} tasks)"

    def filter_by_status(self, status: TaskStatus) -> Generator[Task, None, None]:
        logger.info("Filtering by status=%s", status.name)
        for task in self._tasks:
            if task.status == status:
                logger.info("filter_by_status matched task id=%s", task.id)
                yield task

    def filter_by_priority(self, priority: Priority) -> Generator[Task, None, None]:
        logger.info("Filtering by priority=%s", priority.name)
        for task in self._tasks:
            if task.priority == priority:
                logger.info("filter_by_priority matched task id=%s", task.id)
                yield task

    def filter_by(
        self,
        *,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
    ) -> Generator[Task, None, None]:
        logger.info(
            "Filtering by combined params: status=%s priority=%s",
            getattr(status, "name", None),
            getattr(priority, "name", None),
        )
        for task in self._tasks:
            if status is not None and task.status != status:
                continue
            if priority is not None and task.priority != priority:
                continue
            logger.info("filter_by matched task id=%s", task.id)
            yield task

    def process(self, status: Optional[TaskStatus] = None) -> Generator[Task, None, None]:
        logger.info("Processing started for status=%s", getattr(status, "name", None))
        source = self._tasks if status is None else list(self.filter_by_status(status))

        for task in source:
            task.status = TaskStatus.IN_PROGRESS
            logger.info("Task moved to IN_PROGRESS: id=%s", task.id)
            yield task
            task.status = TaskStatus.DONE
            logger.info("Task moved to DONE: id=%s", task.id)

    def payloads(self) -> Generator[object, None, None]:
        logger.info("Payload generator requested")
        for task in self._tasks:
            yield task.payload

    def ids(self) -> Generator[str, None, None]:
        logger.info("ID generator requested")
        for task in self._tasks:
            yield task.id