import asyncio
import logging
from typing import Protocol, runtime_checkable

from src.errors import ExecutorError, ExecutorNotStartedError, TaskProcessingError
from src.models import Task

logger = logging.getLogger(__name__)

@runtime_checkable
class TaskHandler(Protocol):
    async def handle(self, task: Task) -> None:
        """Обработать одну задачу."""
        ...


class AsyncTaskExecutor:
    def __init__(self, workers: int = 2) -> None:
        self._workers = workers
        self._queue: asyncio.Queue[Task | None] = asyncio.Queue()
        self._handler: TaskHandler | None = None
        self._worker_tasks: list[asyncio.Task] = []
        self._running: bool = False
        self._errors: list[TaskProcessingError] = []


    def register(self, handler: object) -> None:
        if not isinstance(handler, TaskHandler):
            raise TypeError(
                f"{handler!r} не реализует протокол TaskHandler "
                f"(нужен метод async def handle(task))"
            )
        self._handler = handler
        logger.info("Handler registered: %s", type(handler).__name__)

    async def submit(self, task: Task) -> None:
        if not self._running:
            raise ExecutorNotStartedError(
                "AsyncTaskExecutor не запущен — используй `async with`"
            )
        await self._queue.put(task)
        logger.info("Task submitted: id=%s", task.id)

    async def wait_all(self) -> None:
        if self._queue:
            await self._queue.join()

    @property
    def errors(self) -> list[TaskProcessingError]:
        return list(self._errors)

    async def __aenter__(self) -> "AsyncTaskExecutor":
        self._queue = asyncio.Queue()
        self._running = True
        self._worker_tasks = [
            asyncio.create_task(self._worker_loop(f"worker-{i}"))
            for i in range(self._workers)
        ]
        logger.info("AsyncTaskExecutor started (%d workers)", self._workers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        for _ in self._worker_tasks:
            await self._queue.put(None)

        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._running = False
        logger.info(
            "AsyncTaskExecutor stopped. Errors: %d", len(self._errors)
        )
        return False


    async def _worker_loop(self, name: str) -> None:
        """Основной цикл воркера: забирает задачи из очереди и обрабатывает."""
        logger.info("[%s] started", name)
        while True:
            task = await self._queue.get()
            if task is None:
                self._queue.task_done()
                break
            try:
                if self._handler is None:
                    raise ExecutorError("handler не зарегистрирован")
                await self._handler.handle(task)
                logger.info("[%s] task id=%s done", name, task.id)
            except Exception as exc:
                error = TaskProcessingError(task, exc)
                self._errors.append(error)
                logger.error("[%s] task id=%s error: %s", name, task.id, exc)
            finally:
                self._queue.task_done()
        logger.info("[%s] stopped", name)
