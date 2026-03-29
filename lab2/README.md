# Лабораторная работа №2 — Модель задачи

## Структура проекта

```
lab2/
├── src/
│   └── task_platform/
│       ├── __init__.py      # публичный API пакета
│       └── task.py          # модель Task, дескрипторы, исключения
├── tests/
│   └── test_task.py         # pytest-тесты (покрытие ≥ 80 %)
├── main.py                  # точка входа / демо-сценарий
└── pyproject.toml           # конфиг pytest и coverage
```

## Запуск демо

```bash
PYTHONPATH=src python main.py
```

## Запуск тестов

```bash
pytest -v --cov
```
