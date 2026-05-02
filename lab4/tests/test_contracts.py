import pytest
from src.contracts import Executor
from src.executors import DatabaseExecutor, EmailExecutor, LoggingExecutor, RetryExecutor


@pytest.mark.parametrize("executor_cls", [
    LoggingExecutor, EmailExecutor, DatabaseExecutor, RetryExecutor
])
def test_executor_protocol(executor_cls):
    executor = executor_cls()
    assert isinstance(executor, Executor), (
        f"{executor_cls.__name__} не соответствует протоколу Executor"
    )


@pytest.mark.parametrize("executor_cls", [
    LoggingExecutor, EmailExecutor, DatabaseExecutor, RetryExecutor
])
def test_executor_has_name(executor_cls):
    executor = executor_cls()
    assert isinstance(executor.name, str)
    assert len(executor.name) > 0


def test_random_object_not_executor():
    class Fake:
        name = "fake"

    assert not isinstance(Fake(), Executor)
