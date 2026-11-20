"""Очистка всех таблиц БД перед повторным заполнением (seed).

Запуск из корня проекта:
    python -m scripts.reset_db
"""
from sqlalchemy import text

from src.database import Base, SessionLocal, engine
from src import models  # noqa: F401  (регистрирует все модели в Base.metadata)


def reset_db() -> None:
    session = SessionLocal()
    try:
        # Сначала дочерние таблицы, потом родительские — чтобы не нарушить внешние ключи
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
            print(f"Очищена таблица: {table.name}")

        # В SQLite сбрасываем счётчики id, чтобы нумерация шла с 1
        if engine.dialect.name == "sqlite":
            exists = session.execute(
                text("SELECT name FROM sqlite_master WHERE name = 'sqlite_sequence'")
            ).first()
            if exists:
                session.execute(text("DELETE FROM sqlite_sequence"))

        session.commit()
        print("База данных очищена.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    reset_db()
