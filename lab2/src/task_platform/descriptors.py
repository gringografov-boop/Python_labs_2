from typing import Any
import uuid
from datetime import datetime
from src.task_platform.errors import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
)

class Validated:
    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name  = name
        self.private_name = f"_{name}"

    def __get__(self, obj: Any, objtype: type):
         if obj is None:
             return self
         return obj.__dict__.get(self.private_name)
    
    def __set__(self, obj: Any, value: Any) -> None:
        obj.__dict__[self.private_name] = self.validate(value)

    def validate(self, value: Any) -> Any:
        raise NotImplementedError


class TaskIdDescriptor(Validated):
    def __set__(self, obj: Any, value: Any) -> None:
        if self.private_name in obj.__dict__:
            raise InvalidTaskIdError(
                f"Атрибут '{self.public_name}' нельзя изменить после инициализации."
            )
        super().__set__(obj, value)

    def validate(self, value: Any) -> str:
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, str) and value.strip():
            return value.strip()
        raise InvalidTaskIdError(
            f"task_id должен быть непустой строкой или UUID, получено: {value!r}"
        )


class DescriptionDescriptor(Validated):
    def validate(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise InvalidDescriptionError(
                f"Описание должно быть непустой строкой, получено: {value!r}"
            )
        return value.strip()


class PriorityDescriptor(Validated):
    MIN = 1
    MAX = 10
    def validate(self, value: Any) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidPriorityError(
                f"Приоритет должен быть целым числом, получено: {value!r}"
            )
        if not (self.MIN <= value <= self.MAX):
            raise InvalidPriorityError(
                f"Приоритет должен быть в диапазоне [{self.MIN}, {self.MAX}], "
                f"получено: {value}"
            )
        return value

class ReadonlyTimestamp:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> datetime | None:
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    

class TaskMeta:
    __slots__ = ("created_by", "tags")

    def __init__(self, created_by: str, tags: list[str] | None = None) -> None:
        self.created_by = created_by
        self.tags = tags or []