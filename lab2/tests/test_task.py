import pytest
import uuid
from datetime import datetime

from src.task_platform.task import (
    Task,
    TaskStatus,
)
from src.task_platform.descriptors import (
    TaskIdDescriptor,
    DescriptionDescriptor,
    PriorityDescriptor,
    ReadonlyTimestamp,
)
from src.task_platform.errors import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusTransitionError,
)
@pytest.fixture
def task() -> Task:
    return Task(description="Обработать заказ #42", priority=3)


class TestTaskIdDescriptor:
    def test_accepts_string(self):
        t = Task(description="test", task_id="abc-123")
        assert t.task_id == "abc-123"

    def test_accepts_uuid(self):
        uid = uuid.uuid4()
        t = Task(description="test", task_id=str(uid))
        assert t.task_id == str(uid)

    def test_strips_whitespace(self):
        t = Task(description="test", task_id="  my-id  ")
        assert t.task_id == "my-id"

    def test_auto_generated_if_none(self, task):
        assert task.task_id
        uuid.UUID(task.task_id)

    def test_immutable_after_init(self, task):
        with pytest.raises(InvalidTaskIdError):
            task.task_id = "new-id"

    def test_raises_on_empty_string(self):
        with pytest.raises(InvalidTaskIdError):
            Task(description="test", task_id="   ")

    def test_raises_on_non_string(self):
        with pytest.raises(InvalidTaskIdError):
            Task(description="test", task_id=123)

    def test_class_access_returns_descriptor(self):
        assert isinstance(Task.task_id, TaskIdDescriptor)


class TestDescriptionDescriptor:
    def test_strips_whitespace(self):
        t = Task(description="  обработать  ")
        assert t.description == "обработать"

    def test_raises_on_empty(self):
        with pytest.raises(InvalidDescriptionError):
            Task(description="")

    def test_raises_on_whitespace_only(self):
        with pytest.raises(InvalidDescriptionError):
            Task(description="   ")

    def test_raises_on_non_string(self):
        with pytest.raises(InvalidDescriptionError):
            Task(description=None)  # type: ignore

    def test_mutable(self, task):
        task.description = "Новое описание"
        assert task.description == "Новое описание"

    def test_class_access_returns_descriptor(self):
        assert isinstance(Task.description, DescriptionDescriptor)


class TestPriorityDescriptor:
    def test_valid_boundary_min(self):
        t = Task(description="x", priority=1)
        assert t.priority == 1

    def test_valid_boundary_max(self):
        t = Task(description="x", priority=10)
        assert t.priority == 10

    def test_valid_middle(self, task):
        assert task.priority == 3

    def test_default_is_5(self):
        t = Task(description="x")
        assert t.priority == 5

    def test_raises_below_min(self):
        with pytest.raises(InvalidPriorityError):
            Task(description="x", priority=0)

    def test_raises_above_max(self):
        with pytest.raises(InvalidPriorityError):
            Task(description="x", priority=11)

    def test_raises_on_float(self):
        with pytest.raises(InvalidPriorityError):
            Task(description="x", priority=5.0) 

    def test_raises_on_bool(self):
        with pytest.raises(InvalidPriorityError):
            Task(description="x", priority=True)  

    def test_class_access_returns_descriptor(self):
        assert isinstance(Task.priority, PriorityDescriptor)

class TestReadonlyTimestamp:
    def test_created_at_is_datetime(self, task):
        assert isinstance(task.created_at, datetime)

    def test_created_at_is_recent(self, task):
        from datetime import timezone
        delta = datetime.now() - task.created_at
        assert delta.total_seconds() < 5

    def test_class_access_returns_descriptor(self):
        assert isinstance(Task.created_at, ReadonlyTimestamp)

    def test_non_data_descriptor_loses_to_instance_dict(self, task):
        assert "created_at" in task.__dict__

class TestStatusTransitions:
    def test_initial_status_is_pending(self, task):
        assert task.status == TaskStatus.PENDING

    def test_pending_to_running(self, task):
        task.start()
        assert task.status == TaskStatus.RUNNING

    def test_running_to_done(self, task):
        task.start()
        task.complete()
        assert task.status == TaskStatus.DONE

    def test_pending_to_cancelled(self, task):
        task.cancel()
        assert task.status == TaskStatus.CANCELLED

    def test_running_to_cancelled(self, task):
        task.start()
        task.cancel()
        assert task.status == TaskStatus.CANCELLED

    def test_done_is_terminal(self, task):
        task.start()
        task.complete()
        with pytest.raises(InvalidStatusTransitionError):
            task.complete()

    def test_cancelled_is_terminal(self, task):
        task.cancel()
        with pytest.raises(InvalidStatusTransitionError):
            task.start()

    def test_invalid_type_raises(self, task):
        with pytest.raises(InvalidStatusTransitionError):
            task.status = "running"

    def test_skip_transition_raises(self, task):
        with pytest.raises(InvalidStatusTransitionError):
            task.status = TaskStatus.DONE


class TestIsReady:
    def test_ready_when_pending(self, task):
        assert task.is_ready is True

    def test_not_ready_when_running(self, task):
        task.start()
        assert task.is_ready is False

    def test_not_ready_when_done(self, task):
        task.start()
        task.complete()
        assert task.is_ready is False

    def test_not_ready_when_cancelled(self, task):
        task.cancel()
        assert task.is_ready is False


class TestRepr:
    def test_repr_contains_id(self, task):
        assert task.task_id in repr(task)

    def test_repr_contains_status(self, task):
        assert "pending" in repr(task)
