import logging
from src.models import Task

logger = logging.getLogger(__name__)


class TaskQueueIterator:
    def __init__(self, tasks: list[Task]) -> None:
        self._tasks: list[Task] = list(tasks)
        self._index: int = 0

    def __iter__(self) -> "TaskQueueIterator":
        return self

    def __next__(self) -> Task:
        if self._index >= len(self._tasks):
            raise StopIteration
        task = self._tasks[self._index]
        self._index += 1
        return task
    
class AsyncTaskQueueIterator:
    def __init__(self, tasks):
        self._tasks = list(tasks)
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._tasks):
            raise StopAsyncIteration
        task = self._tasks[self._index]
        self._index += 1
        return task