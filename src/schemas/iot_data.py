import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StationDataCreateSchema(BaseModel):
    field_id: uuid.UUID
    payload: dict[str, int]
    date_time: datetime


class StationDataReadSchema(StationDataCreateSchema):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class SensorDataCreateSchema(BaseModel):
    field_id: uuid.UUID
    sensor_id: int
    payload: dict[str, int]
    date_time: datetime


class SensorDataReadSchema(SensorDataCreateSchema):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class ParamSummarySchema(BaseModel):
    avg: float
    min: float
    max: float


class StationDataSummarySchema(BaseModel):
    field_id: uuid.UUID
    date_from: datetime
    date_to: datetime
    count: int
    params: dict[str, ParamSummarySchema]


class SensorDataSummarySchema(BaseModel):
    field_id: uuid.UUID
    sensor_id: int
    date_from: datetime
    date_to: datetime
    count: int
    params: dict[str, ParamSummarySchema]
