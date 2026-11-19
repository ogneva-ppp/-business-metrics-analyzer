from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class Kpi(Base):
    __tablename__ = "kpi"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False)
    metric_name: Mapped[str] = mapped_column(ForeignKey("metric_settings.metric_name"), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    metric_setting: Mapped["MetricSetting"] = relationship(back_populates="kpis")
