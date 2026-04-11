import pytest
from src.models import Task, TaskStatus, Priority
from src.iterator import TaskQueueIterator


@pytest.fixture
def three_tasks():
    return [
        Task("a", 1, TaskStatus.PENDING, Priority.LOW),
        Task("b", 2, TaskStatus.DONE, Priority.HIGH),
        Task("c", 3, TaskStatus.PENDING, Priority.MEDIUM),
    ]


class TestTaskQueueIterator:
    def test_iter_returns_self(self, three_tasks):
        it = TaskQueueIterator(three_tasks)
        assert iter(it) is it

    def test_next_returns_tasks_in_order(self, three_tasks):
        it = TaskQueueIterator(three_tasks)
        assert next(it).id == "a"
        assert next(it).id == "b"
        assert next(it).id == "c"

    def test_stop_iteration_raised(self, three_tasks):
        it = TaskQueueIterator(three_tasks)
        list(it)
        with pytest.raises(StopIteration):
            next(it)

    def test_empty_iterator(self):
        it = TaskQueueIterator([])
        with pytest.raises(StopIteration):
            next(it)

    def test_list_conversion(self, three_tasks):
        it = TaskQueueIterator(three_tasks)
        result = list(it)
        assert len(result) == 3
        assert result[0].id == "a"

    def test_snapshot_independence(self, three_tasks):
        original = list(three_tasks)
        it = TaskQueueIterator(three_tasks)
        three_tasks.clear()
        result = list(it)
        assert len(result) == 3

    def test_for_loop(self, three_tasks):
        ids = [t.id for t in TaskQueueIterator(three_tasks)]
        assert ids == ["a", "b", "c"]

    def test_next_with_default(self, three_tasks):
        it = TaskQueueIterator(three_tasks)
        list(it)
        assert next(it, None) is None
