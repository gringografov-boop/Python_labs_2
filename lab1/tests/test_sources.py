import json
import tempfile
import unittest
from pathlib import Path

from src.core.models import Task
from src.core.contracts import TaskSource
from src.receiver import TaskReceiver
from src.sources.api import ApiStubTaskSource
from src.sources.file import FileTaskSource
from src.sources.generator import GeneratorTaskSource


class TestTaskModel(unittest.TestCase):
    def test_task_creation_simple(self):
        task = Task(id="test_1", payload="simple_data")

        self.assertEqual(task.id, "test_1")
        self.assertEqual(task.payload, "simple_data")

    def test_task_with_dict_payload(self):
        payload = {"action": "send_email", "user": "test@example.com", "priority": 1}
        task = Task(id="task_2", payload=payload)

        self.assertEqual(task.id, "task_2")
        self.assertIsInstance(task.payload, dict)
        self.assertEqual(task.payload["action"], "send_email")
        self.assertEqual(task.payload["priority"], 1)

    def test_task_with_list_payload(self):
        task = Task(id="task_3", payload=[1, 2, 3, "test"])

        self.assertIsInstance(task.payload, list)
        self.assertEqual(len(task.payload), 4)

    def test_task_with_none_payload(self):
        task = Task(id="task_4", payload=None)

        self.assertEqual(task.id, "task_4")
        self.assertIsNone(task.payload)

    def test_task_equality(self):
        task1 = Task(id="1", payload="data")
        task2 = Task(id="1", payload="data")
        task3 = Task(id="2", payload="data")
        task4 = Task(id="1", payload="other_data")

        self.assertEqual(task1, task2)

        self.assertNotEqual(task1, task3)

        self.assertNotEqual(task1, task4)

    def test_task_repr(self):
        task = Task(id="repr_test", payload="data")
        task_repr = repr(task)

        self.assertIn("Task", task_repr)
        self.assertIn("repr_test", task_repr)

class TestGeneratorTaskSource(unittest.TestCase):
    def test_generator_isinstance_protocol(self):
        source = GeneratorTaskSource(count=5)
        self.assertTrue(isinstance(source, TaskSource))

    def test_generator_correct_count(self):
        for count in [0, 1, 5, 10, 100]:
            with self.subTest(count=count):
                source = GeneratorTaskSource(count=count)
                tasks = list(source.get_tasks())
                self.assertEqual(len(tasks), count)

    def test_generator_task_structure(self):
        source = GeneratorTaskSource(count=3)
        tasks = list(source.get_tasks())

        self.assertEqual(tasks[0].id, "gen_0")
        self.assertIsInstance(tasks[0].payload, dict)
        self.assertIn("status", tasks[0].payload)
        self.assertIn("iteration", tasks[0].payload)
        self.assertEqual(tasks[0].payload["iteration"], 0)

        self.assertEqual(tasks[2].id, "gen_2")
        self.assertEqual(tasks[2].payload["iteration"], 2)

    def test_generator_returns_iterable(self):
        source = GeneratorTaskSource(count=5)
        result = source.get_tasks()

        self.assertTrue(hasattr(result, '__iter__'))

        tasks1 = list(source.get_tasks())
        tasks2 = list(source.get_tasks())

        self.assertEqual(len(tasks1), 5)
        self.assertEqual(len(tasks2), 5)

    def test_generator_unique_ids(self):
        source = GeneratorTaskSource(count=10)
        tasks = list(source.get_tasks())

        ids = [task.id for task in tasks]
        unique_ids = set(ids)

        self.assertEqual(len(ids), len(unique_ids), "ID задач должны быть уникальны")

class TestApiStubTaskSource(unittest.TestCase):
    def test_api_isinstance_protocol(self):
        source = ApiStubTaskSource()
        self.assertTrue(isinstance(source, TaskSource))

    def test_api_returns_tasks(self):
        source = ApiStubTaskSource()
        tasks = list(source.get_tasks())

        self.assertGreater(len(tasks), 0, "API должен вернуть хотя бы одну задачу")

    def test_api_task_structure(self):
        source = ApiStubTaskSource()
        tasks = list(source.get_tasks())

        for task in tasks:
            with self.subTest(task_id=task.id):
                self.assertIsInstance(task, Task)
                self.assertTrue(task.id.startswith("api_"))
                self.assertIsNotNone(task.payload)

    def test_api_consistent_output(self):
        source = ApiStubTaskSource()

        tasks1 = list(source.get_tasks())
        tasks2 = list(source.get_tasks())

        self.assertEqual(len(tasks1), len(tasks2))

        ids1 = [t.id for t in tasks1]
        ids2 = [t.id for t in tasks2]
        self.assertEqual(ids1, ids2)

    def test_api_no_init_params(self):
        try:
            source = ApiStubTaskSource()
            tasks = list(source.get_tasks())
            self.assertIsInstance(tasks, list)
        except TypeError:
            self.fail("ApiStubTaskSource не должен требовать параметров")

class TestFileTaskSource(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, encoding='utf-8', suffix='.json'
        )

        self.test_data = [
            {"id": "file_1", "payload": "test_data_1"},
            {"id": "file_2", "payload": {"key": "value", "count": 42}},
        ]

        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_file_isinstance_protocol(self):
        source = FileTaskSource(self.temp_file.name)
        self.assertTrue(isinstance(source, TaskSource))

    def test_file_reads_tasks(self):
        source = FileTaskSource(self.temp_file.name)
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, "file_1")
        self.assertEqual(tasks[0].payload, "test_data_1")

    def test_file_complex_payload(self):
        source = FileTaskSource(self.temp_file.name)
        tasks = list(source.get_tasks())

        self.assertIsInstance(tasks[1].payload, dict)
        self.assertEqual(tasks[1].payload["key"], "value")
        self.assertEqual(tasks[1].payload["count"], 42)

    def test_file_not_found(self):
        source = FileTaskSource("nonexistent_file_12345.json")

        with self.assertRaises(FileNotFoundError):
            list(source.get_tasks())

    def test_file_invalid_json(self):
        temp_invalid = tempfile.NamedTemporaryFile(
            mode='w', delete=False, encoding='utf-8', suffix='.json'
        )
        temp_invalid.write("invalid json content {]}")
        temp_invalid.close()

        try:
            source = FileTaskSource(temp_invalid.name)

            with self.assertRaises(json.JSONDecodeError):
                list(source.get_tasks())
        finally:
            Path(temp_invalid.name).unlink(missing_ok=True)

    def test_file_empty_array(self):
        temp_empty = tempfile.NamedTemporaryFile(
            mode='w', delete=False, encoding='utf-8', suffix='.json'
        )
        json.dump([], temp_empty)
        temp_empty.close()

        try:
            source = FileTaskSource(temp_empty.name)
            tasks = list(source.get_tasks())

            self.assertEqual(len(tasks), 0)
        finally:
            Path(temp_empty.name).unlink(missing_ok=True)

class InvalidSource:
    def wrong_method(self):
        return []


class TestTaskReceiver(unittest.TestCase):

    def setUp(self):
        self.receiver = TaskReceiver()

    def test_receiver_initialization(self):
        self.assertEqual(len(self.receiver._sources), 0)

    def test_register_valid_source(self):
        source = GeneratorTaskSource(count=5)
        self.receiver.register_source(source)

        self.assertEqual(len(self.receiver._sources), 1)

    def test_register_invalid_source_raises_error(self):
        invalid_source = InvalidSource()

        with self.assertRaises(TypeError) as context:
            self.receiver.register_source(invalid_source)

        error_message = str(context.exception)
        self.assertIn("InvalidSource", error_message)
        self.assertIn("не реализует протокол TaskSource", error_message)

    def test_register_multiple_sources(self):
        self.receiver.register_source(GeneratorTaskSource(3))
        self.receiver.register_source(ApiStubTaskSource())
        self.receiver.register_source(GeneratorTaskSource(2))

        self.assertEqual(len(self.receiver._sources), 3)

    def test_receive_tasks_from_single_source(self):
        self.receiver.register_source(GeneratorTaskSource(count=5))
        tasks = self.receiver.receive_tasks()

        self.assertEqual(len(tasks), 5)
        self.assertIsInstance(tasks[0], Task)

    def test_receive_tasks_from_multiple_sources(self):
        self.receiver.register_source(GeneratorTaskSource(count=3))
        self.receiver.register_source(ApiStubTaskSource())

        tasks = self.receiver.receive_tasks()

        self.assertGreaterEqual(len(tasks), 6)

    def test_receive_tasks_empty_receiver(self):
        tasks = self.receiver.receive_tasks()

        self.assertEqual(len(tasks), 0)
        self.assertIsInstance(tasks, list)

    def test_clear_sources(self):

        self.receiver.register_source(GeneratorTaskSource(5))
        self.receiver.register_source(ApiStubTaskSource())
        self.assertEqual(len(self.receiver._sources), 2)

        self.receiver.clear_sources()

        self.assertEqual(len(self.receiver._sources), 0)
        self.assertEqual(len(self.receiver.receive_tasks()), 0)

    def test_integration_all_sources(self):
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, encoding='utf-8', suffix='.json'
        )
        json.dump([{"id": "file_1", "payload": "file_data"}], temp_file)
        temp_file.close()

        try:
            self.receiver.register_source(GeneratorTaskSource(count=2))
            self.receiver.register_source(ApiStubTaskSource())
            self.receiver.register_source(FileTaskSource(temp_file.name))

            tasks = self.receiver.receive_tasks()

            self.assertEqual(len(tasks), 6)

            ids = [task.id for task in tasks]

            has_gen = any(task_id.startswith("gen_") for task_id in ids)
            has_api = any(task_id.startswith("api_") for task_id in ids)
            has_file = any(task_id.startswith("file_") for task_id in ids)

            self.assertTrue(has_gen, "Нет задач от GeneratorTaskSource")
            self.assertTrue(has_api, "Нет задач от ApiStubTaskSource")
            self.assertTrue(has_file, "Нет задач от FileTaskSource")

        finally:
            Path(temp_file.name).unlink(missing_ok=True)

    def test_receiver_tasks_isolation(self):
        self.receiver.register_source(GeneratorTaskSource(count=3))

        tasks1 = self.receiver.receive_tasks()
        tasks2 = self.receiver.receive_tasks()

        self.assertIsNot(tasks1, tasks2)

        self.assertEqual(len(tasks1), len(tasks2))


if __name__ == '__main__':
    unittest.main()