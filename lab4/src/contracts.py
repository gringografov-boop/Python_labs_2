from typing import Protocol, runtime_checkable
from src.models import Task


@runtime_checkable
class Executor(Protocol):
    async def execute(self, task: Task) -> None:
        """Обработать задачу. Должен быть корутиной."""
        ...

    @property
    def name(self) -> str:
        """Человекочитаемое имя исполнителя."""
        ...
