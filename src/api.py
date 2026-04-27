import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, status

from src.auth_dep import TokenPayload, require_user
from src.schemas.iot_data import (
    SensorDataReadSchema,
    SensorDataSummarySchema,
    StationDataReadSchema,
    StationDataSummarySchema,
)
from src.schemas.stations import (
    DashboardSchema,
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
    summary="Регистрация станции",
    description=(
        "Создаёт станцию `(hardware_id, field_id, org_id из JWT)`. "
        "Если переданы `latitude/longitude` — опционально проверяет point-in-polygon "
        "контура поля через fields-service; результат в `coords_match_field` "
        "(`null`, если fields-service недоступен)."
    ),
)
async def register_station(
    body: StationRegisterSchema,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
    authorization: Annotated[str, Header(alias="Authorization")],
):
    station, coords_match = await service.register_station(body, user.org, authorization)
    return StationRegisterResponseSchema(station=station, coords_match_field=coords_match)


@router.get(
    "/stations",
    response_model=list[StationReadSchema],
    summary="Мои станции",
)
async def list_my_stations(
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.list_my_stations(user.org)


@router.get(
    "/stations/{field_id}",
    response_model=StationReadSchema,
    summary="Станция на поле",
)
async def get_my_station(
    field_id: uuid.UUID,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_my_station(field_id, user.org)


@router.put(
    "/stations/{field_id}",
    response_model=StationReadSchema,
    summary="Обновить станцию (name/lat/lon)",
)
async def update_station(
    field_id: uuid.UUID,
    body: StationUpdateSchema,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.update_station(field_id, body, user.org)


@router.delete(
    "/stations/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить станцию (CASCADE: данные тоже)",
)
async def delete_station(
    field_id: uuid.UUID,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    await service.delete_station(field_id, user.org)


@router.get(
    "/fields/{field_id}/stations",
    response_model=list[StationOnFieldSchema],
    summary="Станции на поле (для карты)",
    description="Список с координатами и `online` — для отображения маркеров на карте поля.",
)
async def list_stations_on_field(
    field_id: uuid.UUID,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.list_stations_on_field(field_id, user.org)


@router.get(
    "/fields/{field_id}/data/last",
    response_model=StationDataReadSchema,
    summary="Последний пакет станции",
)
async def get_last_station_data_by_field(
    field_id: uuid.UUID,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_last_station_data_by_field(field_id, user.org)


@router.get(
    "/fields/{field_id}/data/history",
    response_model=list[StationDataReadSchema],
    summary="История пакетов станции",
    description="Сортировка по `date_time` ASC. Границы `date_from`/`date_to` включительные.",
)
async def get_station_history_by_field(
    field_id: uuid.UUID,
    date_from: Annotated[datetime, Query()],
    date_to: Annotated[datetime, Query()],
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_station_history_by_field(
        field_id, date_from, date_to, user.org
    )


@router.get(
    "/fields/{field_id}/data/summary",
    response_model=StationDataSummarySchema,
    summary="Агрегаты по станции (avg/min/max)",
)
async def get_station_data_summary_by_field(
    field_id: uuid.UUID,
    date_from: Annotated[datetime, Query()],
    date_to: Annotated[datetime, Query()],
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_station_data_summary_by_field(
        field_id, date_from, date_to, user.org
    )


@router.get(
    "/fields/{field_id}/sensors",
    response_model=list[int],
    summary="Список sensor_id для станции на поле",
)
async def list_sensor_ids_by_field(
    field_id: uuid.UUID,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.list_sensor_ids_by_field(field_id, user.org)


@router.get(
    "/fields/{field_id}/sensors/{sensor_id}/data/last",
    response_model=SensorDataReadSchema,
    summary="Последний пакет датчика",
)
async def get_last_sensor_data_by_field(
    field_id: uuid.UUID,
    sensor_id: int,
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_last_sensor_data_by_field(field_id, sensor_id, user.org)


@router.get(
    "/fields/{field_id}/sensors/{sensor_id}/data/history",
    response_model=list[SensorDataReadSchema],
    summary="История пакетов датчика",
)
async def get_sensor_history_by_field(
    field_id: uuid.UUID,
    sensor_id: int,
    date_from: Annotated[datetime, Query()],
    date_to: Annotated[datetime, Query()],
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_sensor_history_by_field(
        field_id, sensor_id, date_from, date_to, user.org
    )


@router.get(
    "/fields/{field_id}/sensors/{sensor_id}/data/summary",
    response_model=SensorDataSummarySchema,
    summary="Агрегаты по датчику (avg/min/max)",
)
async def get_sensor_data_summary_by_field(
    field_id: uuid.UUID,
    sensor_id: int,
    date_from: Annotated[datetime, Query()],
    date_to: Annotated[datetime, Query()],
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_sensor_data_summary_by_field(
        field_id, sensor_id, date_from, date_to, user.org
    )


@router.get(
    "/dashboard",
    response_model=DashboardSchema,
    summary="Дашборд организации",
    description=(
        "Один запрос для главной страницы IoT: все станции + `online` + "
        "последний пакет станции + список датчиков с их последними пакетами."
    ),
)
async def get_dashboard(
    user: Annotated[TokenPayload, Depends(require_user)],
    service: Annotated[IoTService, Depends()],
):
    return await service.get_dashboard(user.org)
