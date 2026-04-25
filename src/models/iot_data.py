import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StationData(Base):
    __tablename__ = "station_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stations.hardware_id", ondelete="CASCADE"),
        index=True,
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    date_time: Mapped[datetime] = mapped_column(DateTime, index=True)


class SensorData(Base):
    __tablename__ = "sensor_data"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stations.hardware_id", ondelete="CASCADE"),
        index=True,
    )
    sensor_id: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    date_time: Mapped[datetime] = mapped_column(DateTime, index=True)
