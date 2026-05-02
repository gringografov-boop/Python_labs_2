from __future__ import annotations
from src.models import Task


class ExecutorError(Exception):
    """Базовый класс ошибок исполнителя."""


class TaskProcessingError(ExecutorError):
    """Ошибка при обработке конкретной задачи."""

    def __init__(self, task: Task, cause: Exception) -> None:
        self.task = task
        self.cause = cause
        super().__init__(f"Task {task.id!r} failed: {cause}")


class ExecutorNotStartedError(ExecutorError):
    """Попытка использовать исполнитель вне контекстного менеджера."""
