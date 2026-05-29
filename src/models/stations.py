import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Double, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Station(Base):
    field_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    hardware_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    polling_interval_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
