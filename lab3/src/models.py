import logging
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    FAILED = auto()


class Priority(int, Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10


@dataclass
class Task:
    id: str
    payload: object
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM

    def __post_init__(self) -> None:
        logger.info(
            "Task created: id=%s status=%s priority=%s",
            self.id,
            self.status.name,
            self.priority.name,
        )

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, priority={self.priority.name}, status={self.status.name})"