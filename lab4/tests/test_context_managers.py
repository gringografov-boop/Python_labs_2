"""Тесты контекстных менеджеров и generator-методов."""
import pytest
from src.context_managers import QueueSession, task_logger, task_processor_gen
from src.executors import DatabaseExecutor
from src.models import Priority, Task, TaskStatus
from src.queue import TaskQueue


def make_task(tid: str, status: TaskStatus = TaskStatus.PENDING) -> Task:
    return Task(tid, f"payload-{tid}", status, Priority.MEDIUM)


def make_queue(*ids: str) -> TaskQueue:
    q = TaskQueue()
    for tid in ids:
        q.enqueue(make_task(tid))
    return q


# ──────────────────────────────────────────────────────────
#  DatabaseExecutor как контекстный менеджер
# ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_database_executor_context_manager():
    with DatabaseExecutor() as db:
        assert db._connected is True
        await db.execute(make_task("db1"))
    assert db._connected is False


def test_database_executor_without_context_raises():
    db = DatabaseExecutor()
    import asyncio
    with pytest.raises(RuntimeError):
        asyncio.get_event_loop().run_until_complete(db.execute(make_task("db2")))


def test_database_executor_exit_on_exception():
    db = DatabaseExecutor()
    try:
        with db:
            raise ValueError("boom")
    except ValueError:
        pass
    assert db._connected is False


# ──────────────────────────────────────────────────────────
#  QueueSession
# ──────────────────────────────────────────────────────────

def test_queue_session_returns_queue():
    q = make_queue("s1", "s2")
    with QueueSession(q) as session_q:
        assert session_q is q


def test_queue_session_marks_failed_on_error():
    q = make_queue("f1", "f2")
    try:
        with QueueSession(q):
            raise RuntimeError("simulated error")
    except RuntimeError:
        pass
    statuses = [t.status for t in q]
    assert all(s == TaskStatus.FAILED for s in statuses)


def test_queue_session_no_side_effect_on_success():
    q = make_queue("ok1")
    with QueueSession(q):
        pass
    # без ошибок — статусы не должны измениться
    assert list(q)[0].status == TaskStatus.PENDING


# ──────────────────────────────────────────────────────────
#  @contextmanager task_logger
# ──────────────────────────────────────────────────────────

def test_task_logger_yields_task():
    task = make_task("tl1")
    with task_logger(task) as t:
        assert t is task


def test_task_logger_reraises_exception():
    task = make_task("tl2")
    with pytest.raises(ValueError):
        with task_logger(task):
            raise ValueError("test")


# ──────────────────────────────────────────────────────────
#  generator.send / .throw / .close
# ──────────────────────────────────────────────────────────

def test_generator_send_done():
    q = make_queue("g1", "g2")
    gen = task_processor_gen(q)
    t1 = next(gen)
    assert t1.id == "g1"
    try:
        gen.send(True)   # первую принять
    except StopIteration:
        pass
    assert t1.status == TaskStatus.DONE


def test_generator_send_failed():
    q = make_queue("g3")
    gen = task_processor_gen(q)
    t = next(gen)
    try:
        gen.send(False)
    except StopIteration:
        pass
    assert t.status == TaskStatus.FAILED


def test_generator_throw():
    q = make_queue("g4", "g5")
    gen = task_processor_gen(q)
    next(gen)
    with pytest.raises(ValueError):
        gen.throw(ValueError("test throw"))


def test_generator_close():
    q = make_queue("g6", "g7", "g8")
    gen = task_processor_gen(q)
    next(gen)
    gen.close()   # не должно бросать исключений
