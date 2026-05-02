import asyncio
import logging
from typing import Iterable

from src.contracts import Executor
from src.models import Task, TaskStatus
from src.queue import TaskQueue

logger = logging.getLogger(__name__)


class TaskHandler:
    def __init__(self, executors: Iterable[Executor]) -> None:
        self._executors: list[Executor] = list(executors)
        logger.info(
            "TaskHandler created with executors: %s",
            [e.name for e in self._executors],
        )

    async def handle_task(self, task: Task) -> None:
        logger.info(">>> handle_task started: id=%s", task.id)
        task.status = TaskStatus.IN_PROGRESS
        try:
            for executor in self._executors:
                await executor.execute(task)
            task.status = TaskStatus.DONE
            logger.info("<<< handle_task done: id=%s", task.id)
        except Exception as exc:
            task.status = TaskStatus.FAILED
            logger.error("handle_task FAILED: id=%s error=%s", task.id, exc)

    async def handle_all(self, queue: TaskQueue) -> None:
        logger.info("handle_all started, queue size=%d", len(queue))
        for task in queue.filter_by_status(TaskStatus.PENDING):
            await self.handle_task(task)
        logger.info("handle_all finished")

    async def handle_concurrent(self, queue: TaskQueue) -> None:
        tasks = list(queue.filter_by_status(TaskStatus.PENDING))
        logger.info("handle_concurrent started, %d tasks to run", len(tasks))
        await asyncio.gather(*[self.handle_task(t) for t in tasks])
        logger.info("handle_concurrent finished")
