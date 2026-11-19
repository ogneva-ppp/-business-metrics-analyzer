"""Воспроизводимое наполнение БД данными для Business Metrics Analyzer.

Запуск из корня репозитория: python -m scripts.seed_data
Перед повторным наполнением выполнить scripts/reset_db.py.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Kpi, MetricSetting, Product, Report, Sale, User
from src.queries import get_kpi_dashboard

Faker.seed(42)
fake = Faker("ru_RU")
rng = random.Random(42)


def seed_users(session: Session, count: int = 10) -> list[User]:
    # Гарантируем минимум одного менеджера для ссылочной целостности продаж.
    roles = ["manager", "director", "analyst", "admin"]
    users = [
        User(username=fake.unique.user_name(), email=fake.unique.email(),
             password_hash=fake.sha256(), role=roles[i % len(roles)])
        for i in range(count)
    ]
    session.add_all(users)
    session.flush()
    return users


def seed_products(session: Session, count: int = 20) -> list[Product]:
    categories = ["Электроника", "Одежда", "Продукты", "Бытовая химия", "Книги"]
    products = [
        Product(name=fake.catch_phrase()[:100], category=rng.choice(categories),
                price=Decimal(str(rng.randint(10000, 1000000))) / 100)
        for _ in range(count)
    ]
    session.add_all(products)
    session.flush()
    return products


def seed_metric_settings(session: Session) -> list[MetricSetting]:
    settings = [
        MetricSetting(metric_name="revenue", formula="SUM(revenue)", is_active=True),
        MetricSetting(metric_name="profitability", formula="(revenue - cost) / revenue * 100", is_active=True),
        MetricSetting(metric_name="avg_check", formula="revenue / orders_count", is_active=True),
        MetricSetting(metric_name="conversion", formula="orders_count / visits * 100", is_active=False),
    ]
    session.add_all(settings)
    session.flush()
    return settings


def seed_sales(session: Session, users: list[User], products: list[Product], count: int = 500) -> list[Sale]:
    managers = [u for u in users if u.role in ("manager", "director")]
    if not managers or not products:
        raise ValueError("Для генерации продаж необходимы менеджер и товар")
    sales = []
    for _ in range(count):
        sale_date = date(2026, 1, 1) + timedelta(days=rng.randint(0, 180))
        revenue = Decimal(rng.randint(100000, 10000000)) / 100
        cost_ratio = Decimal(rng.randint(40, 90)) / 100
        sales.append(Sale(
            sale_date=sale_date, month=sale_date.strftime("%Y-%m"),
            revenue=revenue, cost=(revenue * cost_ratio).quantize(Decimal("0.01")),
            orders_count=rng.randint(1, 20), manager_id=rng.choice(managers).id,
            product_id=rng.choice(products).id,
        ))
    session.add_all(sales)
    session.flush()
    return sales


def seed_kpis(session: Session) -> list[Kpi]:
    periods = session.scalars(select(Sale.month).distinct().order_by(Sale.month)).all()
    rows = []
    for period in periods:
        dashboard = get_kpi_dashboard(session, period)
        for metric_name in ("revenue", "profitability", "avg_check"):
            source_key = {"revenue": "total_revenue", "profitability": "profitability", "avg_check": "avg_check"}[metric_name]
            rows.append(Kpi(period=period, metric_name=metric_name,
                            value=Decimal(str(dashboard[source_key])).quantize(Decimal("0.0001"))))
    session.add_all(rows)
    session.flush()
    return rows


def seed_reports(session: Session, users: list[User]) -> list[Report]:
    reports = [
        Report(report_type="monthly_sales", period="2026-01",
               file_path="reports/monthly_sales_2026-01.csv", created_by=users[0].id),
        Report(report_type="kpi_summary", period="2026-02",
               file_path="reports/kpi_summary_2026-02.csv", created_by=users[1].id),
    ]
    session.add_all(reports)
    session.flush()
    return reports


def main() -> None:
    with SessionLocal() as session:
        # Защита от дублирования при случайном повторном запуске.
        if session.scalar(select(func.count()).select_from(User)):
            print("В таблице users уже есть данные. Сначала выполните reset_db.py.")
            return
        try:
            users = seed_users(session)
            products = seed_products(session)
            settings = seed_metric_settings(session)
            sales = seed_sales(session, users, products)
            kpis = seed_kpis(session)
            reports = seed_reports(session, users)
            session.commit()
        except Exception:
            session.rollback()
            raise
        print(f"Создано: пользователей {len(users)}, товаров {len(products)}, "
              f"продаж {len(sales)}, настроек метрик {len(settings)}, "
              f"KPI {len(kpis)}, отчётов {len(reports)}")
        print("Выручка за 2026-01:", get_kpi_dashboard(session, "2026-01")["total_revenue"])


if __name__ == "__main__":
    main()
