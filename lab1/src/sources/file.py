import json
import logging
from pathlib import Path
from typing import Iterable

from src.core.models import Task

logger = logging.getLogger(__name__)
 
class FileTaskSource:
    def __init__(self, filepath: str) -> None:
        self.filepath = Path(filepath)

    def get_tasks(self) -> Iterable[Task]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error("Файл не найден: %s", self.filepath)
            raise
        except json.JSONDecodeError as e:
            logger.error("Некорректный JSON в файле %s: %s", self.filepath, e)
            raise

        logger.debug("Загружено %d задач из файла %s", len(data), self.filepath)
        return [Task(id=item['id'], payload=item['payload']) for item in data]