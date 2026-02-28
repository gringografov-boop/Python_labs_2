from typing import Iterable, Protocol, runtime_checkable
from src.core.models import Task

@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterable[Task]:
        ...