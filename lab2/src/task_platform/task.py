from __future__ import annotations

import logging
import uuid
from datetime import datetime
from enum import Enum
from src.task_platform.descriptors import (
    TaskIdDescriptor,
    DescriptionDescriptor,
    PriorityDescriptor,
    ReadonlyTimestamp,
)
from src.task_platform.errors import InvalidStatusTransitionError


logger = logging.getLogger(__name__)

__all__ = [
    "Task",
    "TaskStatus",
]

class TaskStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    DONE      = "done"
    CANCELLED = "cancelled"


_ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING:   {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.RUNNING:   {TaskStatus.DONE, TaskStatus.CANCELLED},
    TaskStatus.DONE:      set(),
    TaskStatus.CANCELLED: set(),
}

class Task:
    task_id = TaskIdDescriptor()
    description = DescriptionDescriptor()
    priority = PriorityDescriptor()

    created_at = ReadonlyTimestamp()   
    def __init__(
        self,
        description: str,
        priority: int = 5,
        task_id: str | None = None,
    ) -> None:
        self.task_id     = task_id if task_id is not None else str(uuid.uuid4())
        self.description = description
        self.priority    = priority

        self.__dict__["_status"] = TaskStatus.PENDING

        self.__dict__["created_at"] = datetime.now()

        logger.info(
            "Task created",
            extra={"task_id": self.task_id, "priority": self.priority},
        )

    @property
    def status(self) -> TaskStatus:
        return self.__dict__["_status"]

    @status.setter
    def status(self, new_status: TaskStatus) -> None:
        if not isinstance(new_status, TaskStatus):
            raise InvalidStatusTransitionError(
                f"Ожидается TaskStatus, получено: {new_status!r}"
            )
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                f"Переход '{self.status.value}' → '{new_status.value}' недопустим. "
                f"Допустимые: {[s.value for s in allowed] or 'нет переходов'}"
            )
        old = self.status
        self.__dict__["_status"] = new_status
        logger.info(
            "Task status changed",
            extra={"task_id": self.task_id, "from": old.value, "to": new_status.value},
        )

    @property
    def is_ready(self) -> bool:
        return self.status == TaskStatus.PENDING

    def start(self) -> None:
        self.status = TaskStatus.RUNNING

    def complete(self) -> None:
        self.status = TaskStatus.DONE

    def cancel(self) -> None:
        self.status = TaskStatus.CANCELLED

    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id!r}, description={self.description!r}, "
            f"priority={self.priority}, status={self.status.value!r})"
        )
