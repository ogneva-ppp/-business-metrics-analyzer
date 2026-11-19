"""Запросы Business Metrics Analyzer через SQLAlchemy 2.0."""
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Product, Sale, User


def get_sales_by_month(session: Session, month: str) -> list[Sale]:
    """Продажи за месяц, отсортированные по дате."""
    stmt = select(Sale).where(Sale.month == month).order_by(Sale.sale_date, Sale.id)
    return list(session.scalars(stmt).all())


def get_total_revenue(session: Session, month: str) -> Decimal:
    """Суммарная выручка за месяц."""
    stmt = select(func.sum(Sale.revenue)).where(Sale.month == month)
    return session.execute(stmt).scalar_one() or Decimal("0.00")


def get_sales_with_manager_and_product(session: Session, month: str):
    """Продажи с логином менеджера и названием товара (JOIN)."""
    stmt = (
        select(Sale, User.username, Product.name)
        .join(User, Sale.manager_id == User.id)
        .join(Product, Sale.product_id == Product.id)
        .where(Sale.month == month)
        .order_by(Sale.sale_date, Sale.id)
    )
    return session.execute(stmt).all()


def get_kpi_dashboard(session: Session, month: str) -> dict:
    """Сводные показатели продаж за месяц (формула среднего чека из задания)."""
    stmt = select(
        func.sum(Sale.revenue).label("total_revenue"),
        func.sum(Sale.cost).label("total_cost"),
        func.sum(Sale.orders_count).label("total_orders"),
        func.avg(Sale.revenue / func.nullif(Sale.orders_count, 0)).label("avg_check"),
    ).where(Sale.month == month)
    row = session.execute(stmt).one()
    total_revenue = row.total_revenue or Decimal("0.00")
    total_cost = row.total_cost or Decimal("0.00")
    profitability = (
        (total_revenue - total_cost) / total_revenue * 100
        if total_revenue > 0 else Decimal("0.00")
    )
    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_orders": row.total_orders or 0,
        "avg_check": Decimal(str(row.avg_check)) if row.avg_check is not None else Decimal("0.00"),
        "profitability": profitability,
    }
