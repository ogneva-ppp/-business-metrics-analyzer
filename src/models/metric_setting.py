from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class MetricSetting(Base):
    __tablename__ = "metric_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    formula: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    kpis: Mapped[list["Kpi"]] = relationship(back_populates="metric_setting")
