import json
from pathlib import Path
from typing import Iterable

from src.core.models import Task


class FileTaskSource:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def get_tasks(self) -> Iterable[Task]:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Task(id=item['id'], payload=item['payload']) for item in data]