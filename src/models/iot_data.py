import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StationData(Base):
    __tablename__ = "station_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    field_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("stations.field_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    date_time: Mapped[datetime] = mapped_column(DateTime, index=True)


class SensorData(Base):
    __tablename__ = "sensor_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    field_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("stations.field_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sensor_id: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    date_time: Mapped[datetime] = mapped_column(DateTime, index=True)
