from typing import List
from src.core.models import Task 
from src.core.contracts import TaskSource

class TaskReceiver:
    def __init__(self) -> None:
        self._sources: List[TaskSource] = []

    def register_source(self, source: TaskSource) -> None:
        if not isinstance(source, TaskSource):
            raise TypeError(
                f"Объект типа {type(source).__name__} не реализует протокол TaskSource."
            )
        self._sources.append(source)

    def receive_tasks(self) -> List[Task]:
        tasks: List[Task] = []
        for source in self._sources:
            tasks.extend(source.get_tasks())
        return tasks

    def clear_sources(self) -> None:
        self._sources.clear()