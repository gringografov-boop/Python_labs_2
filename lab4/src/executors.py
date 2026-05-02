import asyncio
import logging
import random as _random_module
from typing import Callable

from src.models import Task

logger = logging.getLogger(__name__)


class LoggingExecutor:
    name: str = "LoggingExecutor"

    async def execute(self, task: Task) -> None:
        logger.info("[%s] Logging task id=%s payload=%s", self.name, task.id, task.payload)
        await asyncio.sleep(0)


class EmailExecutor:
    name: str = "EmailExecutor"

    async def execute(self, task: Task) -> None:
        delay = _random_module.uniform(0.05, 0.15)
        logger.info("[%s] Sending email for task id=%s …", self.name, task.id)
        await asyncio.sleep(delay)
        logger.info("[%s] Email sent for task id=%s (%.2fs)", self.name, task.id, delay)


class DatabaseExecutor:

    name: str = "DatabaseExecutor"

    async def execute(self, task: Task) -> None:
        delay = _random_module.uniform(0.1, 0.3)
        logger.info("[%s] Saving task id=%s to DB …", self.name, task.id)
        await asyncio.sleep(delay)
        logger.info("[%s] Task id=%s saved (%.2fs)", self.name, task.id, delay)


class RetryExecutor:
    name: str = "RetryExecutor"
    max_retries: int = 2

    def __init__(self, _rand_fn: Callable[[], float] | None = None) -> None:
        self._rand_fn = _rand_fn or _random_module.random

    async def execute(self, task: Task) -> None:
        for attempt in range(1, self.max_retries + 2):
            fail = self._rand_fn() < 0.4
            logger.info("[%s] Attempt %d for task id=%s", self.name, attempt, task.id)
            await asyncio.sleep(0.05)
            if not fail:
                logger.info("[%s] Task id=%s completed on attempt %d", self.name, task.id, attempt)
                return
            if attempt <= self.max_retries:
                logger.warning("[%s] Attempt %d failed, retrying …", self.name, attempt)
        logger.error("[%s] Task id=%s FAILED after %d attempts", self.name, task.id, self.max_retries + 1)
        raise RuntimeError(f"Task {task.id!r} failed after {self.max_retries + 1} attempts")
