import types
import pytest
from src.models import Task, TaskStatus, Priority
from src.queue import TaskQueue
from src.iterator import TaskQueueIterator


class TestEnqueueDequeue:
    def test_enqueue_increases_len(self):
        q = TaskQueue()
        assert len(q) == 0
        q.enqueue(Task("x", "d"))
        assert len(q) == 1

    def test_enqueue_wrong_type_raises(self):
        with pytest.raises(TypeError, match="Expected Task"):
            TaskQueue().enqueue("not a task")

    def test_dequeue_returns_first(self, queue):
        first = queue.dequeue()
        assert first.id == "t1"
        assert len(queue) == 4

    def test_dequeue_fifo_order(self, queue, sample_tasks):
        for expected in sample_tasks:
            got = queue.dequeue()
            assert got.id == expected.id

    def test_dequeue_empty_raises(self):
        with pytest.raises(IndexError):
            TaskQueue().dequeue()

    def test_repr(self, queue):
        assert "5 tasks" in repr(queue)


class TestIteration:
    def test_iter_returns_task_queue_iterator(self, queue):
        assert isinstance(iter(queue), TaskQueueIterator)

    def test_for_loop_all_tasks(self, queue, sample_tasks):
        result = [t.id for t in queue]
        assert result == [t.id for t in sample_tasks]

    def test_repeatable_iteration(self, queue):
        first = list(queue)
        second = list(queue)
        assert [t.id for t in first] == [t.id for t in second]

    def test_each_iter_is_new_object(self, queue):
        it1 = iter(queue)
        it2 = iter(queue)
        assert it1 is not it2

    def test_nested_iteration(self, queue):
        outer_ids = []
        inner_counts = []
        for outer in queue:
            outer_ids.append(outer.id)
            inner_counts.append(sum(1 for _ in queue))
        assert len(outer_ids) == 5
        assert all(c == 5 for c in inner_counts)

    def test_list_builtin(self, queue):
        assert len(list(queue)) == 5

    def test_sum_builtin(self, queue):
        assert sum(1 for _ in queue) == 5

    def test_empty_queue_iteration(self):
        q = TaskQueue()
        assert list(q) == []


class TestFilterByStatus:
    def test_pending(self, queue):
        result = list(queue.filter_by_status(TaskStatus.PENDING))
        assert len(result) == 3
        assert all(t.status == TaskStatus.PENDING for t in result)

    def test_done(self, queue):
        result = list(queue.filter_by_status(TaskStatus.DONE))
        assert len(result) == 1
        assert result[0].id == "t3"

    def test_in_progress_empty(self, queue):
        assert list(queue.filter_by_status(TaskStatus.IN_PROGRESS)) == []

    def test_returns_generator(self, queue):
        assert isinstance(queue.filter_by_status(TaskStatus.PENDING), types.GeneratorType)

    def test_lazy_first_element(self, queue):
        gen = queue.filter_by_status(TaskStatus.PENDING)
        first = next(gen)
        assert first.id == "t1"


class TestFilterByPriority:
    def test_high_priority(self, queue):
        result = list(queue.filter_by_priority(Priority.HIGH))
        assert len(result) == 2
        assert all(t.priority == Priority.HIGH for t in result)

    def test_low_priority(self, queue):
        result = list(queue.filter_by_priority(Priority.LOW))
        assert len(result) == 1
        assert result[0].id == "t1"

    def test_returns_generator(self, queue):
        assert isinstance(queue.filter_by_priority(Priority.HIGH), types.GeneratorType)


class TestFilterBy:
    def test_combined_pending_high(self, queue):
        result = list(queue.filter_by(status=TaskStatus.PENDING, priority=Priority.HIGH))
        assert len(result) == 1
        assert result[0].id == "t2"

    def test_only_status(self, queue):
        result = list(queue.filter_by(status=TaskStatus.DONE))
        assert len(result) == 1

    def test_only_priority(self, queue):
        result = list(queue.filter_by(priority=Priority.MEDIUM))
        assert len(result) == 2

    def test_no_params_returns_all(self, queue):
        assert len(list(queue.filter_by())) == 5

    def test_no_match_returns_empty(self, queue):
        result = list(queue.filter_by(status=TaskStatus.IN_PROGRESS, priority=Priority.HIGH))
        assert result == []

    def test_returns_generator(self, queue):
        assert isinstance(queue.filter_by(), types.GeneratorType)


class TestProcess:
    def test_sets_in_progress_during_yield(self, queue):
        for task in queue.process(status=TaskStatus.PENDING):
            assert task.status == TaskStatus.IN_PROGRESS

    def test_sets_done_after_yield(self, queue):
        list(queue.process(status=TaskStatus.PENDING))
        done = list(queue.filter_by_status(TaskStatus.DONE))
        assert len(done) == 4  # 1 DONE + 3 PENDING processed

    def test_process_all_no_filter(self, queue):
        seen = [t.id for t in queue.process()]
        assert len(seen) == 5

    def test_returns_generator(self, queue):
        assert isinstance(queue.process(), types.GeneratorType)

    def test_process_empty_status(self, queue):
        result = list(queue.process(status=TaskStatus.IN_PROGRESS))
        assert result == []


class TestHelperGenerators:
    def test_payloads(self, queue, sample_tasks):
        assert list(queue.payloads()) == [t.payload for t in sample_tasks]

    def test_ids(self, queue, sample_tasks):
        assert list(queue.ids()) == [t.id for t in sample_tasks]

    def test_payloads_is_generator(self, queue):
        assert isinstance(queue.payloads(), types.GeneratorType)

    def test_ids_is_generator(self, queue):
        assert isinstance(queue.ids(), types.GeneratorType)


class TestLargeVolume:
    def test_10k_tasks_iteration(self):
        q = TaskQueue()
        n = 10_000
        for i in range(n):
            q.enqueue(Task(str(i), i, TaskStatus.PENDING, Priority.LOW))
        assert sum(1 for _ in q) == n

    def test_10k_filter(self):
        q = TaskQueue()
        for i in range(10_000):
            s = TaskStatus.PENDING if i % 2 == 0 else TaskStatus.DONE
            q.enqueue(Task(str(i), i, s))
        assert len(list(q.filter_by_status(TaskStatus.PENDING))) == 5_000
