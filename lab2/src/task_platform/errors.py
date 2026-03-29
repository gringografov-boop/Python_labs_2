class TaskError(Exception):
    """Базовое исключение для ошибок модели задачи."""


class InvalidTaskIdError(TaskError):
    """Идентификатор задачи некорректен."""


class InvalidDescriptionError(TaskError):
    """Описание задачи некорректно."""


class InvalidPriorityError(TaskError):
    """Приоритет задачи некорректен."""


class InvalidStatusTransitionError(TaskError):
    """Недопустимый переход между статусами задачи."""