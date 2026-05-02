"""Тесты AsyncTaskExecutor (asyncio.Queue, async with, create_task, gather)."""
import asyncio
import pytest
from src.async_executor import AsyncTaskExecutor, TaskHandler
from src.errors import ExecutorNotStartedError, TaskProcessingError
from src.models import Priority, Task, TaskStatus


def make_task(tid: str, priority: int = 1) -> Task:
    return Task(tid, f"payload-{tid}", TaskStatus.PENDING, Priority.MEDIUM)


class OkHandler:
    """Простой обработчик — просто помечает задачу как DONE."""
    async def handle(self, task: Task) -> None:
        await asyncio.sleep(0)
        task.status = TaskStatus.DONE


class FailingHandler:
    """Обработчик, который всегда падает."""
    async def handle(self, task: Task) -> None:
        raise ValueError(f"fail for {task.id}")


# ── Protocol ────────────────────────────────────────────────────────────────

def test_task_handler_protocol():
    assert isinstance(OkHandler(), TaskHandler)


def test_non_handler_raises_on_register():
    class NoHandle:
        pass
    with pytest.raises(TypeError):
        AsyncTaskExecutor().register(NoHandle())


# ── async with ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_executor_submit_and_process():
    tasks = [make_task(f"t{i}") for i in range(5)]
    async with AsyncTaskExecutor(workers=2) as ex:
        ex.register(OkHandler())
        for t in tasks:
            await ex.submit(t)
        await ex.wait_all()
    assert all(t.status == TaskStatus.DONE for t in tasks)


@pytest.mark.asyncio
async def test_executor_collects_errors():
    tasks = [make_task(f"e{i}") for i in range(3)]
    async with AsyncTaskExecutor(workers=2) as ex:
        ex.register(FailingHandler())
        for t in tasks:
            await ex.submit(t)
        await ex.wait_all()
    assert len(ex.errors) == 3
    assert all(isinstance(e, TaskProcessingError) for e in ex.errors)


@pytest.mark.asyncio
async def test_executor_submit_outside_context_raises():
    ex = AsyncTaskExecutor()
    with pytest.raises(ExecutorNotStartedError):
        await ex.submit(make_task("x"))


@pytest.mark.asyncio
async def test_executor_no_handler_logs_error():
    tasks = [make_task("nh1")]
    async with AsyncTaskExecutor(workers=1) as ex:
        # не регистрируем handler
        for t in tasks:
            await ex.submit(t)
        await ex.wait_all()
    assert len(ex.errors) == 1


@pytest.mark.asyncio
async def test_executor_multiple_workers_concurrent():
    """Проверяем, что несколько воркеров обрабатывают конкурентно."""
    import time
    tasks = [make_task(f"c{i}") for i in range(4)]

    class SlowHandler:
        async def handle(self, task: Task) -> None:
            await asyncio.sleep(0.05)
            task.status = TaskStatus.DONE

    start = time.monotonic()
    async with AsyncTaskExecutor(workers=4) as ex:
        ex.register(SlowHandler())
        for t in tasks:
            await ex.submit(t)
        await ex.wait_all()
    elapsed = time.monotonic() - start
    # 4 задачи по 0.05s параллельно должны уложиться << 4*0.05=0.2s
    assert elapsed < 0.15


# ── @asynccontextmanager ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_async_task_timer():
    from src.context_managers import async_task_timer
    async with async_task_timer("test"):
        await asyncio.sleep(0.01)
