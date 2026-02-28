import unittest

from src.core.models import Task
from src.core.contracts import TaskSource

class ValidSource:

    def get_tasks(self):
        return [Task(id="valid_1", payload="test_data")]


class InvalidSourceNoMethod:

    def fetch_data(self):
        return []


class InvalidSourceWrongSignature:

    def get_tasks(self, required_param):  # Требует параметр
        return []


class TestTaskSourceProtocol(unittest.TestCase):

    def test_protocol_with_valid_source(self):
        source = ValidSource()
        self.assertTrue(
            isinstance(source, TaskSource),

        )

    def test_protocol_with_invalid_source(self):
        source = InvalidSourceNoMethod()
        self.assertFalse(
            isinstance(source, TaskSource),
        )

    def test_protocol_duck_typing(self):
        source = ValidSource()

        self.assertNotIn(
            TaskSource,
            type(source).__mro__,
        )

        self.assertTrue(isinstance(source, TaskSource))

    def test_protocol_method_call(self):
        source = ValidSource()
        tasks = list(source.get_tasks())

        self.assertEqual(len(tasks), 1)
        self.assertIsInstance(tasks[0], Task)
        self.assertEqual(tasks[0].id, "valid_1")

    def test_protocol_with_builtin_types(self):
        test_objects = [[], {}, "string", 42, None, object()]

        for obj in test_objects:
            with self.subTest(obj=obj):
                self.assertFalse(
                    isinstance(obj, TaskSource),
                    f"{type(obj).__name__} не должен удовлетворять TaskSource"
                )

    def test_protocol_runtime_checkable(self):
        source = ValidSource()

        try:
            result = isinstance(source, TaskSource)
            self.assertTrue(result)
        except TypeError as e:
            self.fail(f"@runtime_checkable не работает: {e}")


class TestDuckTypingPrinciple(unittest.TestCase):
    def test_multiple_implementations_without_inheritance(self):
        class SourceA:
            def get_tasks(self):
                return [Task("a1", "data_a")]

        class SourceB:
            def get_tasks(self):
                return [Task("b1", "data_b")]

        self.assertTrue(isinstance(SourceA(), TaskSource))
        self.assertTrue(isinstance(SourceB(), TaskSource))

        self.assertEqual(SourceA.__bases__, (object,))
        self.assertEqual(SourceB.__bases__, (object,))

    def test_method_implementation_matters_not_declaration(self):
        class ImplicitSource:
            def get_tasks(self):
                return []

        source = ImplicitSource()

        self.assertTrue(hasattr(source, 'get_tasks'))
        self.assertTrue(callable(getattr(source, 'get_tasks')))
        self.assertTrue(isinstance(source, TaskSource))


if __name__ == '__main__':
    unittest.main()