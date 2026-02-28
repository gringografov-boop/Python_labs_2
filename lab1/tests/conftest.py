import json
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_json_file():
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', delete=False, encoding='utf-8', suffix='.json'
    )

    test_data = [
        {"id": "file_1", "payload": "test_data_1"},
        {"id": "file_2", "payload": {"key": "value"}},
    ]

    json.dump(test_data, temp_file)
    temp_file.close()

    file_path = Path(temp_file.name)

    yield file_path

    file_path.unlink(missing_ok=True)


@pytest.fixture
def sample_tasks_data():
    return [
        {"id": "task_1", "payload": "Simple payload"},
        {"id": "task_2", "payload": {"action": "send_email", "user": "test@example.com"}},
        {"id": "task_3", "payload": None},
    ]