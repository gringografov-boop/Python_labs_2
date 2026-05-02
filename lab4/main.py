import asyncio
import logging

from src.async_executor import AsyncTaskExecutor
from src.context_managers import (
    QueueSession,
    async_task_timer,
    task_logger,
    task_processor_gen,
)
from src.executors import DatabaseExecutor, EmailExecutor, LoggingExecutor, RetryExecutor
from src.handler import TaskHandler
from src.models import Priority, Task, TaskStatus
from src.queue import TaskQueue


def build_queue() -> TaskQueue:
    q = TaskQueue()
    q.enqueue(Task("t1", "Обработать заказ #001",  TaskStatus.PENDING, Priority.HIGH))
    q.enqueue(Task("t2", "Отправить уведомление",  TaskStatus.PENDING, Priority.MEDIUM))
    q.enqueue(Task("t3", "Пересчитать статистику", TaskStatus.PENDING, Priority.LOW))
    q.enqueue(Task("t4", "Обновить профиль",       TaskStatus.PENDING, Priority.MEDIUM))
    return q


def sep(title: str) -> None:
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)


def print_statuses(queue: TaskQueue) -> None:
    for t in queue:
        print(f"  [{t.status.name:8}] {t.id} — {t.payload}")



async def demo_sequential(queue: TaskQueue) -> None:
    sep("1. ПОСЛЕДОВАТЕЛЬНАЯ ОБРАБОТКА (handle_all)")
    handler = TaskHandler([LoggingExecutor(), EmailExecutor()])
    await handler.handle_all(queue)
    print("\nСтатусы:")
    print_statuses(queue)



async def demo_concurrent(queue: TaskQueue) -> None:
    sep("2. КОНКУРЕНТНАЯ ОБРАБОТКА (asyncio.gather)")
    handler = TaskHandler([LoggingExecutor(), RetryExecutor()])
    await handler.handle_concurrent(queue)
    print("\nСтатусы:")
    print_statuses(queue)


async def demo_context_manager_class(queue: TaskQueue) -> None:
    sep("3. with __enter__/__exit__ (DatabaseExecutor)")
    with DatabaseExecutor() as db_exec:
        handler = TaskHandler([LoggingExecutor(), db_exec])
        await handler.handle_all(queue)
    print("\nСтатусы:")
    print_statuses(queue)


async def demo_contextmanager(queue: TaskQueue) -> None:
    sep("4. @contextmanager — логирование каждой задачи")
    async for task in queue.afilter_by_status(TaskStatus.PENDING):
        with task_logger(task) as t:
            await asyncio.sleep(0.02)
            t.status = TaskStatus.DONE
    print("\nСтатусы:")
    print_statuses(queue)


async def demo_queue_session(queue: TaskQueue) -> None:
    sep("5. QueueSession — транзакция над очередью")
    with QueueSession(queue) as q:
        handler = TaskHandler([LoggingExecutor()])
        await handler.handle_concurrent(q)
    print("\nСтатусы:")
    print_statuses(queue)


async def demo_async_executor(queue: TaskQueue) -> None:
    sep("6. async with AsyncTaskExecutor (asyncio.Queue + create_task)")

    class PrintHandler:
        async def handle(self, task: Task) -> None:
            await asyncio.sleep(0.03)
            task.status = TaskStatus.DONE
            print(f"  [PrintHandler] обработал {task.id}")

    async with AsyncTaskExecutor(workers=2) as executor:
        executor.register(PrintHandler())
        async for task in queue.afilter_by_status(TaskStatus.PENDING):
            await executor.submit(task)
        await executor.wait_all()

    if executor.errors:
        print(f"  Ошибок: {len(executor.errors)}")
    print("\nСтатусы:")
    print_statuses(queue)


async def demo_async_contextmanager(queue: TaskQueue) -> None:
    sep("7. @asynccontextmanager — замер времени конкурентной обработки")
    handler = TaskHandler([LoggingExecutor()])
    async with async_task_timer("конкурентная обработка"):
        await handler.handle_concurrent(queue)
    print("\nСтатусы:")
    print_statuses(queue)


def demo_generator_methods(queue: TaskQueue) -> None:
    sep("8. generator.send / .throw / .close")

    gen = task_processor_gen(queue)

    task = next(gen)
    print(f"  next()   → получена: {task.id}")
    try:
        task2 = gen.send(True)
        print(f"  send(True)  → {task.id} = DONE, следующая: {task2.id}")
    except StopIteration:
        pass

    try:
        gen.throw(ValueError("тестовый throw"))
    except ValueError as e:
        print(f"  throw(ValueError) → поймали: {e}")

    gen2 = task_processor_gen(queue)
    t = next(gen2)
    print(f"\n  gen2: next() → {t.id}")
    gen2.close()
    print("  gen2.close() → генератор закрыт")

    print("\nСтатусы:")
    print_statuses(queue)


async def main() -> None:
    await demo_sequential(build_queue())
    await demo_concurrent(build_queue())
    await demo_context_manager_class(build_queue())
    await demo_contextmanager(build_queue())
    await demo_queue_session(build_queue())
    await demo_async_executor(build_queue())
    await demo_async_contextmanager(build_queue())
    demo_generator_methods(build_queue())

    sep("ГОТОВО")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    asyncio.run(main())