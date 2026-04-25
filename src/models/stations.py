import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Double, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Station(Base):
    hardware_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    field_id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, nullable=False)
    org_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
