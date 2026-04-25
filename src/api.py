import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status

from src.auth_dep import TokenPayload, require_user
from src.schemas.iot_data import SensorDataReadSchema, StationDataReadSchema
from src.schemas.stations import (
    StationOnFieldSchema,
    StationReadSchema,
    StationRegisterResponseSchema,
    StationRegisterSchema,
    StationUpdateSchema,
)
from src.service import IoTService

router = APIRouter(prefix="/api/iot", tags=["iot"])


@router.post(
    "/stations",
    response_model=StationRegisterResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_station(
    body: StationRegisterSchema,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
    authorization: Annotated[str, Header(alias="Authorization")],
):
    station, coords_match = await service.register_station(body, user.org, authorization)
    return StationRegisterResponseSchema(station=station, coords_match_field=coords_match)


@router.get("/stations", response_model=list[StationReadSchema])
async def list_my_stations(
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.list_my_stations(user.org)


@router.get("/stations/{hardware_id}", response_model=StationReadSchema)
async def get_my_station(
    hardware_id: int,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_my_station(hardware_id, user.org)


@router.put("/stations/{hardware_id}", response_model=StationReadSchema)
async def update_station(
    hardware_id: int,
    body: StationUpdateSchema,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.update_station(hardware_id, body, user.org)


@router.delete("/stations/{hardware_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(
    hardware_id: int,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    await service.delete_station(hardware_id, user.org)


@router.get(
    "/fields/{field_id}/stations",
    response_model=list[StationOnFieldSchema],
)
async def list_stations_on_field(
    field_id: uuid.UUID,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.list_stations_on_field(field_id, user.org)


@router.get("/stations/{hardware_id}/sensors", response_model=list[int])
async def list_sensor_ids(
    hardware_id: int,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.list_sensor_ids(hardware_id, user.org)


@router.get(
    "/stations/{hardware_id}/data/last",
    response_model=StationDataReadSchema,
)
async def get_last_station_data(
    hardware_id: int,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_last_station_data(hardware_id, user.org)


@router.get(
    "/stations/{hardware_id}/data/history",
    response_model=list[StationDataReadSchema],
)
async def get_station_history(
    hardware_id: int,
    date_from: Annotated[datetime, Query()],
    date_to: Annotated[datetime, Query()],
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_station_history(hardware_id, date_from, date_to, user.org)


@router.get(
    "/stations/{hardware_id}/sensors/{sensor_id}/data/last",
    response_model=SensorDataReadSchema,
)
async def get_last_sensor_data(
    hardware_id: int,
    sensor_id: int,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_last_sensor_data(hardware_id, sensor_id, user.org)


@router.get(
    "/stations/{hardware_id}/sensors/{sensor_id}/data/history",
    response_model=list[SensorDataReadSchema],
)
async def get_sensor_history(
    hardware_id: int,
    sensor_id: int,
    date_from: Annotated[datetime, Query()],
    date_to: Annotated[datetime, Query()],
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_sensor_history(
        hardware_id, sensor_id, date_from, date_to, user.org
    )
