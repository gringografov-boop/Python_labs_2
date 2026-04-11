import logging
from src.models import Task

logger = logging.getLogger(__name__)


class TaskQueueIterator:
    def __init__(self, tasks: list[Task]) -> None:
        self._tasks: list[Task] = list(tasks)
        self._index: int = 0
        logger.info("TaskQueueIterator created for %d tasks", len(self._tasks))

    def __iter__(self) -> "TaskQueueIterator":
        logger.info("Iterator returned itself")
        return self

    def __next__(self) -> Task:
        if self._index >= len(self._tasks):
            logger.info("Iterator reached end and raised StopIteration")
            raise StopIteration

        task = self._tasks[self._index]
        self._index += 1
        logger.info("Iterator returned task id=%s", task.id)
        return task