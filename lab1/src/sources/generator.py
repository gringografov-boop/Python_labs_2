from typing import Iterable
from src.core.models import Task


class GeneratorTaskSource:
    def __init__(self, count: int) -> None:
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for i in range(self.count):
            yield Task(
                id=f"gen_{i}",
                payload={"status": "generated", "iteration": i}
            )