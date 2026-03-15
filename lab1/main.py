import logging
from src.core.models import Task
from src.receiver import TaskReceiver
from src.sources.api import ApiStubTaskSource
from src.sources.generator import GeneratorTaskSource

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:

    receiver = TaskReceiver()
    receiver.register_source(GeneratorTaskSource(count=3))
    receiver.register_source(ApiStubTaskSource())

    tasks: list[Task] = receiver.receive_tasks()

    print(f"Собрано задач: {len(tasks)}")


if __name__ == "__main__":
    main()
