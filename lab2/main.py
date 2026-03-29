import logging

from src.task_platform.task import Task, TaskStatus
from src.task_platform.errors import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusTransitionError,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s task_id=%(task_id)s %(message)s",
)


def main() -> None:
    logger = logging.getLogger(__name__)

    task = Task(description="Обработать заказ #42", priority=3)
    logger.info("Создана новая задача", extra={"task_id": task.task_id})

    try:
        task.start()
        logger.info("Задача запущена", extra={"task_id": task.task_id})

        task.complete()
        logger.info("Задача завершена", extra={"task_id": task.task_id})
    except InvalidStatusTransitionError as e:
        logger.error(
            "Ошибка перехода статуса: %s", e, extra={"task_id": task.task_id}
        )

    try:
        task.task_id = "hacked"
    except InvalidTaskIdError as e:
        logger.warning(
            "Попытка изменить task_id: %s", e, extra={"task_id": task.task_id}
        )

    try:
        Task(description="test", priority=99)
    except InvalidPriorityError as e:
        logger.warning(
            "Некорректный приоритет при создании: %s", e, extra={"task_id": "-"}
        )

    try:
        Task(description="   ")
    except InvalidDescriptionError as e:
        logger.warning(
            "Некорректное описание при создании: %s", e, extra={"task_id": "-"}
        )

    tasks = [
        Task(description="Отправить уведомление", priority=8),
        Task(description="Пересчитать статистику", priority=2),
        Task(description="Проверить состояние ресурса", priority=5),
    ]

    for t in tasks:
        logger.info("Создана задача", extra={"task_id": t.task_id})
        t.start()
        logger.info("Задача запущена", extra={"task_id": t.task_id})


if __name__ == "__main__":
    main()