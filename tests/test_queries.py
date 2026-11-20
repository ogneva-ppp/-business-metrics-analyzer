"""Тесты четырёх запросов на изолированной SQLite в памяти."""
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.models import Product, Sale, User
from src.queries import (
    get_kpi_dashboard,
    get_sales_by_month,
    get_sales_with_manager_and_product,
    get_total_revenue,
)


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        yield db
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sample_sales(session):
    manager = User(username="mgr1", email="mgr1@example.com", password_hash="test", role="manager")
    product = Product(name="Товар 1", category="Категория A", price=Decimal("100.00"))
    session.add_all([manager, product])
    session.flush()
    session.add_all([
        Sale(sale_date=date(2026, 1, 15), month="2026-01", revenue=Decimal("1000.00"),
             cost=Decimal("700.00"), orders_count=5, manager_id=manager.id, product_id=product.id),
        Sale(sale_date=date(2026, 1, 20), month="2026-01", revenue=Decimal("500.00"),
             cost=Decimal("300.00"), orders_count=5, manager_id=manager.id, product_id=product.id),
        Sale(sale_date=date(2026, 2, 1), month="2026-02", revenue=Decimal("300.00"),
             cost=Decimal("100.00"), orders_count=2, manager_id=manager.id, product_id=product.id),
    ])
    session.commit()
    return manager, product


def test_get_sales_by_month(session, sample_sales):
    sales = get_sales_by_month(session, "2026-01")
    assert len(sales) == 2
    assert [sale.sale_date for sale in sales] == [date(2026, 1, 15), date(2026, 1, 20)]


def test_get_total_revenue(session, sample_sales):
    assert get_total_revenue(session, "2026-01") == Decimal("1500.00")
    assert get_total_revenue(session, "2026-03") == Decimal("0.00")


def test_get_sales_with_manager_and_product(session, sample_sales):
    rows = get_sales_with_manager_and_product(session, "2026-01")
    assert len(rows) == 2
    assert all(username == "mgr1" and name == "Товар 1" for sale, username, name in rows)


def test_get_kpi_dashboard(session, sample_sales):
    dashboard = get_kpi_dashboard(session, "2026-01")
    assert dashboard["total_revenue"] == Decimal("1500.00")
    assert dashboard["total_cost"] == Decimal("1000.00")
    assert dashboard["total_orders"] == 10
    assert dashboard["avg_check"] == Decimal("150.00")
    assert abs(dashboard["profitability"] - Decimal("33.333333")) < Decimal("0.0001")


def test_empty_month(session, sample_sales):
    assert get_sales_by_month(session, "2026-12") == []
    assert get_sales_with_manager_and_product(session, "2026-12") == []
    dashboard = get_kpi_dashboard(session, "2026-12")
    assert dashboard["total_revenue"] == 0
    assert dashboard["total_orders"] == 0
    assert dashboard["profitability"] == 0
