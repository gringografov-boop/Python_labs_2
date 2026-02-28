from typing import Iterable
from src.core.models import Task
"""
    В реальной системе здесь был бы HTTP-клиент,
    вызовы REST API или gRPC.
"""
class ApiStubTaskSource:
    def get_tasks(self) -> Iterable[Task]:
        api_response = [
            {"task_id": "api_1", "data": "Обработать заказ #1234"},
            {"task_id": "api_2", "data": "Отправить уведомление пользователю"},
            {"task_id": "api_3", "data": "Пересчитать статистику за день"},
        ]

        return [
            Task(id=item["task_id"], payload=item["data"]) 
            for item in api_response
        ]