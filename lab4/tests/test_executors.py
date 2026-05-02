import pytest
from unittest.mock import AsyncMock, patch

from src.executors import DatabaseExecutor, EmailExecutor, LoggingExecutor, RetryExecutor
from src.models import Priority, Task, TaskStatus


def make_task(task_id: str = "t1") -> Task:
    return Task(task_id, "payload", TaskStatus.PENDING, Priority.MEDIUM)


@pytest.mark.asyncio
async def test_logging_executor():
    ex = LoggingExecutor()
    await ex.execute(make_task())


@pytest.mark.asyncio
async def test_email_executor():
    ex = EmailExecutor()
    with patch("src.executors.asyncio.sleep", new_callable=AsyncMock):
        await ex.execute(make_task())


@pytest.mark.asyncio
async def test_database_executor():
    ex = DatabaseExecutor()
    with patch("src.executors.asyncio.sleep", new_callable=AsyncMock):
        await ex.execute(make_task())


@pytest.mark.asyncio
async def test_retry_executor_success():
    """rand_fn() >= 0.4 → fail=False → задача выполняется с первой попытки."""
    ex = RetryExecutor(_rand_fn=lambda: 0.9)   # 0.9 < 0.4 == False → no fail
    with patch("src.executors.asyncio.sleep", new_callable=AsyncMock):
        await ex.execute(make_task())           # не должно бросать


@pytest.mark.asyncio
async def test_retry_executor_always_fails():
    """rand_fn() < 0.4 → fail=True всегда → RuntimeError после всех попыток."""
    ex = RetryExecutor(_rand_fn=lambda: 0.0)   # 0.0 < 0.4 == True → always fail
    with patch("src.executors.asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(RuntimeError):
            await ex.execute(make_task())
