import contextlib
import logging
import time
from typing import AsyncGenerator, Generator

from src.models import Task, TaskStatus
from src.queue import TaskQueue

logger = logging.getLogger(__name__)


class QueueSession:

    def __init__(self, queue: TaskQueue) -> None:
        self._queue = queue
        self._start_time: float = 0.0

    def __enter__(self) -> TaskQueue:
        self._start_time = time.monotonic()
        logger.info("QueueSession opened (%d tasks)", len(self._queue))
        return self._queue

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        elapsed = time.monotonic() - self._start_time
        if exc_type is None:
            logger.info("QueueSession closed successfully in %.3fs", elapsed)
        else:
            logger.error(
                "QueueSession closed with error %s in %.3fs", exc_type.__name__, elapsed
            )
            for task in self._queue.filter_by_status(TaskStatus.PENDING):
                task.status = TaskStatus.FAILED
                logger.warning("Task id=%s marked as FAILED due to session error", task.id)
        return False 

@contextlib.contextmanager
def task_logger(task: Task) -> Generator[Task, None, None]:
    logger.info(">>> task_logger enter: id=%s", task.id)
    start = time.monotonic()
    try:
        yield task
    except Exception as exc:
        logger.error("task_logger caught exception for task id=%s: %s", task.id, exc)
        raise
    finally:
        elapsed = time.monotonic() - start
        logger.info("<<< task_logger exit: id=%s (%.3fs)", task.id, elapsed)

def task_processor_gen(queue: TaskQueue) -> Generator[Task, bool, str]:
    processed = 0
    for task in queue:
        logger.info("[gen] Yielding task id=%s", task.id)
        try:
            success: bool = yield task
        except GeneratorExit:
            logger.info("[gen] GeneratorExit received after %d tasks", processed)
            return f"closed after {processed} tasks"
        except Exception as exc:
            logger.error("[gen] Exception thrown into generator: %s", exc)
            task.status = TaskStatus.FAILED
            raise

        if success:
            task.status = TaskStatus.DONE
            logger.info("[gen] Task id=%s → DONE", task.id)
        else:
            task.status = TaskStatus.FAILED
            logger.info("[gen] Task id=%s → FAILED (rejected)", task.id)
        processed += 1

    return f"completed {processed} tasks"


@contextlib.asynccontextmanager
async def async_task_timer(label: str) -> AsyncGenerator[None, None]:
    import time
    start = time.monotonic()
    logger.info("[async_timer] %s — start", label)
    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        logger.info("[async_timer] %s — %.3fs", label, elapsed)
        print(f"[async_timer] {label}: {elapsed:.3f}s")
