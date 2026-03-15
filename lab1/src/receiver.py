import logging
from typing import List
from src.core.models import Task 
from src.core.contracts import TaskSource

logger = logging.getLogger(__name__)

class TaskReceiver:
    def __init__(self) -> None:
        self._sources: List[TaskSource] = []
        logger.debug("Taskreciever инициализирован")

    def register_source(self, source: TaskSource) -> None:
        if not isinstance(source, TaskSource):
            logger.error("попытка зарегистрировать невалидный источник: %s", type(source).__name__)
            raise TypeError(
                f"Объект типа {type(source).__name__} не реализует протокол TaskSource."
            )
        self._sources.append(source)
        logger.info("Зарегистрирован источник: %s", type(source).__name__)

    def receive_tasks(self) -> List[Task]:
        logger.info("Начало сбора задач из %d источников", len(self._sources))
        tasks: List[Task] = []
        for source in self._sources:
            tasks.extend(source.get_tasks())
        logger.info("Собрано задач: %d", len(tasks))
        return tasks

    def clear_sources(self) -> None:
        logger.debug("Очистка источников")
        self._sources.clear()