# Лабораторная работа №4
## Асинхронный обработчик очереди задач

Продолжение платформы обработки задач. Лабораторная интегрирует механизмы из предыдущих работ и добавляет асинхронную обработку через `async/await` и `asyncio`.

---

## Что реализовано

- **`Executor` (Protocol)** — контракт исполнителя задачи через `typing.Protocol`; не требует наследования (структурная типизация).
- **Четыре выдуманных исполнителя** (без общего базового класса):
  - `LoggingExecutor` — просто логирует задачу;
  - `EmailExecutor` — имитирует отправку e-mail;
  - `DatabaseExecutor` — имитирует запись в БД;
  - `RetryExecutor` — имитирует сбой с повторными попытками.
- **`TaskHandler`** — асинхронный обработчик:
  - `handle_task(task)` — последовательно запускает всех исполнителей;
  - `handle_all(queue)` — обрабатывает все PENDING-задачи последовательно;
  - `handle_concurrent(queue)` — обрабатывает все PENDING-задачи **конкурентно** через `asyncio.gather`.

---

## Структура проекта

```text
lab4/
├── main.py                   # Точка входа, демонстрация
├── README.md
├── pyproject.toml            # конфиг pytest + coverage
├── src/
│   ├── __init__.py
│   ├── models.py             # Task, TaskStatus, Priority (из lab3)
│   ├── iterator.py           # TaskQueueIterator (из lab3)
│   ├── queue.py              # TaskQueue (из lab3)
│   ├── contracts.py          # Protocol Executor
│   ├── executors.py          # Реализации исполнителей
│   └── handler.py            # TaskHandler
└── tests/
    ├── __init__.py
    ├── test_contracts.py     # Проверка Protocol
    ├── test_executors.py     # Тесты каждого исполнителя
    └── test_handler.py       # Тесты TaskHandler
```

---

## Быстрый старт

### Установка зависимостей

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Запуск демонстрации

```bash
PYTHONPATH=src python main.py
```

### Запуск тестов

```bash
PYTHONPATH=src pytest -v --cov=src --cov-report=term-missing
```

---

## Ключевые концепции

| Концепция | Где используется |
|-----------|-----------------|
| `typing.Protocol` | `src/contracts.py` — контракт Executor |
| `async def` / `await` | Все методы исполнителей и `TaskHandler` |
| `asyncio.gather` | `handle_concurrent` — параллельный запуск корутин |
| `asyncio.run` | `main.py` — запуск event loop |
| Итератор / генератор | `TaskQueue.filter_by_status` (из lab3) |
| `TaskStatus` | Смена статусов `PENDING → IN_PROGRESS → DONE/FAILED` |

---

## Как работает обработчик

```
TaskQueue (lab3)
     │
     │  filter_by_status(PENDING)
     ▼
 [Task, Task, Task, …]
     │
     │  asyncio.gather / sequential
     ▼
TaskHandler.handle_task(task)
     │
     ├─► executor1.execute(task)   ─── await ───► I/O имитация
     ├─► executor2.execute(task)   ─── await ───► I/O имитация
     └─► executor3.execute(task)   ─── await ───► I/O имитация
     │
     ▼
 task.status = DONE (или FAILED при исключении)
```
