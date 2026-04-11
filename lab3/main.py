import logging

from src.models import Task, TaskStatus, Priority
from src.queue import TaskQueue



def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    q = TaskQueue()
    q.enqueue(Task("t1", "Обработать заказ", TaskStatus.PENDING, Priority.HIGH))
    q.enqueue(Task("t2", "Отправить уведомление", TaskStatus.PENDING, Priority.MEDIUM))
    q.enqueue(Task("t3", "Пересчитать статистику", TaskStatus.DONE, Priority.LOW))

    list(q)
    list(q.filter_by_status(TaskStatus.PENDING))
    list(q.filter_by_priority(Priority.HIGH))
    list(q.process(status=TaskStatus.PENDING))


if __name__ == "__main__":
    main()