# Лабораторная работа №1: Источники задач и контракты

Реализация подсистемы приёма задач в платформе обработки задач.  
Задачи могут поступать из различных источников, не связанных наследованием, но обязанных реализовывать единый поведенческий контракт.

## Основные компоненты

- **Task** — минимальная структура задачи (`id` + `payload`).
- **TaskSource** — протокол источника задач (контракт через `typing.Protocol`).
- **TaskReceiver** — подсистема приёма с runtime‑проверкой контракта.
- **Источники**:
  - `FileTaskSource`
  - `GeneratorTaskSource`
  - `ApiStubTaskSource`

## Архитектура проекта

```text
LAB1/
├── src/                      # Исходный код платформы
│   ├── __init__.py
│   ├── core/                 # Базовые абстракции
│   │   ├── __init__.py
│   │   ├── models.py         # Модель Task (dataclass)
│   │   └── contracts.py      # Protocol TaskSource
│   ├── sources/              # Реализации источников
│   │   ├── __init__.py
│   │   ├── file.py           # FileTaskSource (JSON)
│   │   ├── generator.py      # GeneratorTaskSource (программный)
│   │   └── api.py            # ApiStubTaskSource (заглушка API)
│   └── receiver.py           # TaskReceiver (приёмник)
├── tests/                    # Автотесты (unittest)
│   ├── __init__.py
│   ├── test_models.py        # Тесты Task
│   ├── test_contracts.py     # Тесты протокола
│   ├── test_sources.py       # Тесты источников
│   └── test_receiver.py      # Тесты приёмника
├── main.py                   # Точка входа (демонстрация)
├── requirements.txt          # Зависимости
├── .gitignore
└── README.md
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск демонстрации

```bash
python main.py
```

### 3. Запуск тестов

```bash
# Все тесты
python -m unittest discover -s tests -v

# Конкретный тест
python -m unittest tests.test_receiver -v
```

## Покрытие тестами

| Модуль        | Описание              | Тесты                           |
|--------------|-----------------------|---------------------------------|
| `models.py`  | Модель `Task`         | Создание, `payload`, равенство |
| `contracts.py` | Протокол `TaskSource` | `isinstance`, duck typing       |
| `file.py`    | Файловый источник     | Чтение JSON, обработка ошибок  |
| `generator.py` | Генератор задач       | Количество, структура          |
| `api.py`     | API‑заглушка          | Структура, стабильность        |
| `receiver.py`| Приёмник задач        | Регистрация, сбор, runtime‑проверка |

Минимальное покрытие: **80%+** (выполнено).
