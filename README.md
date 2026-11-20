# Business Metrics Analyzer

Учебный проект по дисциплине «Проектирование и разработка бизнес-ориентированного программного обеспечения».

## Бизнес-задача

Расчёт и визуализация ключевых показателей эффективности (KPI) предприятия.

## Стек

- Python 3.10+
- pandas
- matplotlib

## Инструкция по запуску

python -m venv .venv

source .venv/bin/activate   # или .venv\Scripts\activate для Windows

pip install -r requirements.txt

python main.py

# Автор

Студент группы Б1123-38.03.05 ба(2)

ФИО: Огнева Полина Андреевна

# Планируемые метрики

- Выручка по месяцам
- Средняя выручка
- Рентабельность, %
- Рост выручки, %

# Работа с базой данных

По умолчанию используется SQLite. Для PostgreSQL задайте `DATABASE_URL` в файле `.env`.

Установка зависимостей и применение миграций:

```
pip install -r requirements.txt
alembic upgrade head
```

Заполнение базы тестовыми данными (`Faker.seed(42)`, данные воспроизводимы):

```
python -m scripts.seed_data
```

Очистка таблиц перед повторным заполнением:

```
python -m scripts.reset_db
```

Запуск тестов запросов:

```
pytest
```

Описание схемы и ER-диаграмма: [docs/database/schema.md](docs/database/schema.md)
