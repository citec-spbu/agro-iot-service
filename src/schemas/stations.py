import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StationRegisterSchema(BaseModel):
    hardware_id: int
    field_id: uuid.UUID
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class StationUpdateSchema(BaseModel):
    field_id: uuid.UUID | None = None
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class StationCreateSchema(StationRegisterSchema):
    org_id: uuid.UUID


class StationReadSchema(BaseModel):
    hardware_id: int
    field_id: uuid.UUID
    org_id: uuid.UUID
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    last_seen_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StationRegisterResponseSchema(BaseModel):
    station: StationReadSchema
    coords_match_field: bool | None = None


class StationOnFieldSchema(BaseModel):
    hardware_id: int
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    last_seen_at: datetime | None = None
    online: bool
    coords_match_field: bool | None = None

    model_config = ConfigDict(from_attributes=True)
