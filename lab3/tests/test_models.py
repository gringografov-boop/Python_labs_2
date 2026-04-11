import pytest
from src.models import Task, TaskStatus, Priority


class TestTaskStatus:
    def test_all_statuses_exist(self):
        assert TaskStatus.PENDING
        assert TaskStatus.IN_PROGRESS
        assert TaskStatus.DONE
        assert TaskStatus.FAILED

    def test_statuses_are_distinct(self):
        statuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.DONE, TaskStatus.FAILED]
        assert len(set(statuses)) == 4


class TestPriority:
    def test_priority_values(self):
        assert Priority.LOW == 1
        assert Priority.MEDIUM == 5
        assert Priority.HIGH == 10

    def test_priority_ordering(self):
        assert Priority.LOW < Priority.MEDIUM < Priority.HIGH

    def test_priority_is_int(self):
        assert isinstance(Priority.HIGH, int)


class TestTask:
    def test_defaults(self):
        t = Task("id1", "data")
        assert t.status == TaskStatus.PENDING
        assert t.priority == Priority.MEDIUM

    def test_custom_fields(self):
        t = Task("x", 42, TaskStatus.DONE, Priority.HIGH)
        assert t.id == "x"
        assert t.payload == 42
        assert t.status == TaskStatus.DONE
        assert t.priority == Priority.HIGH

    def test_repr_contains_id(self):
        t = Task("abc", "data", TaskStatus.PENDING, Priority.LOW)
        r = repr(t)
        assert "abc" in r
        assert "PENDING" in r
        assert "LOW" in r

    def test_task_is_mutable(self):
        t = Task("m", "x")
        t.status = TaskStatus.DONE
        assert t.status == TaskStatus.DONE

    def test_payload_can_be_any_type(self):
        for payload in [None, 42, [1, 2], {"key": "val"}, object()]:
            t = Task("id", payload)
            assert t.payload is payload
