import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StationDataCreateSchema(BaseModel):
    station_id: int
    payload: dict[str, int]
    date_time: datetime


class StationDataReadSchema(StationDataCreateSchema):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class SensorDataCreateSchema(BaseModel):
    station_id: int
    sensor_id: int
    payload: dict[str, int]
    date_time: datetime


class SensorDataReadSchema(SensorDataCreateSchema):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
