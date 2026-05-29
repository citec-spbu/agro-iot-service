import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StationRegisterSchema(BaseModel):
    """Тело `POST /api/iot/stations`."""

    field_id: uuid.UUID
    hardware_id: int
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    polling_interval: float = Field(default=0.5, gt=0)


class StationUpdateSchema(BaseModel):
    """Тело `PUT /api/iot/stations/{field_id}` — ничего что меняет идентичность станции."""

    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    polling_interval: float | None = Field(default=None, gt=0)


class StationReadSchema(BaseModel):
    field_id: uuid.UUID
    hardware_id: int
    org_id: uuid.UUID
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    polling_interval: float = 0.5
    last_seen_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StationRegisterResponseSchema(BaseModel):
    """Ответ регистрации. `coords_match_field` — null, если fields-service недоступен."""

    station: StationReadSchema
    coords_match_field: bool | None = None


class StationOnFieldSchema(BaseModel):
    hardware_id: int
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    polling_interval: float = 0.5
    last_seen_at: datetime | None = None
    online: bool

    model_config = ConfigDict(from_attributes=True)


class StationSensorOverviewSchema(BaseModel):
    sensor_id: int
    last_data: dict | None = None
    last_data_at: datetime | None = None


class StationOverviewSchema(BaseModel):
    station: StationReadSchema
    online: bool
    last_data: dict | None = None
    last_data_at: datetime | None = None
    sensors: list[StationSensorOverviewSchema]


class DashboardSchema(BaseModel):
    stations: list[StationOverviewSchema]
