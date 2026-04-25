import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.clients.fields import FieldContoursClient
from src.config import settings
from src.repositories.exceptions import DBIntegrityError
from src.repositories.uow.base import UnitOfWork
from src.repositories.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from src.schemas.iot_data import SensorDataReadSchema, StationDataReadSchema
from src.schemas.stations import (
    StationOnFieldSchema,
    StationReadSchema,
    StationRegisterSchema,
    StationUpdateSchema,
)


class IoTService:
    def __init__(self, uow: Annotated[UnitOfWork, Depends(SQLAlchemyUnitOfWork)]):
        self.__uow = uow

    async def register_station(
        self,
        body: StationRegisterSchema,
        org_id: uuid.UUID,
        authorization: str,
    ) -> tuple[StationReadSchema, bool | None]:
        coords_match: bool | None = None
        if body.latitude is not None and body.longitude is not None:
            client = FieldContoursClient()
            coords_match = await client.point_in_field(
                body.field_id, body.latitude, body.longitude, authorization
            )

        async with self.__uow:
            try:
                station = await self.__uow.stations.create(
                    {
                        "hardware_id": body.hardware_id,
                        "field_id": body.field_id,
                        "org_id": org_id,
                        "name": body.name,
                        "latitude": body.latitude,
                        "longitude": body.longitude,
                    }
                )
            except DBIntegrityError as exc:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Station with this hardware_id or field_id already exists",
                ) from exc
            await self.__uow.commit()
            schema = StationReadSchema.model_validate(station, from_attributes=True)
        return schema, coords_match

    async def list_my_stations(self, org_id: uuid.UUID) -> list[StationReadSchema]:
        async with self.__uow:
            rows = await self.__uow.stations.read_many(org_id=org_id)
            return [
                StationReadSchema.model_validate(r, from_attributes=True) for r in rows
            ]

    async def get_my_station(
        self, hardware_id: int, org_id: uuid.UUID
    ) -> StationReadSchema:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            return StationReadSchema.model_validate(station, from_attributes=True)

    async def update_station(
        self,
        hardware_id: int,
        body: StationUpdateSchema,
        org_id: uuid.UUID,
    ) -> StationReadSchema:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            patch = body.model_dump(exclude_unset=True)
            for key, value in patch.items():
                setattr(station, key, value)
            await self.__uow.commit()
            return StationReadSchema.model_validate(station, from_attributes=True)

    async def delete_station(self, hardware_id: int, org_id: uuid.UUID) -> None:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            await self.__uow.stations.delete(hardware_id=hardware_id)
            await self.__uow.commit()

    async def list_stations_on_field(
        self, field_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[StationOnFieldSchema]:
        threshold = datetime.now(timezone.utc) - timedelta(
            seconds=settings.ONLINE_THRESHOLD_SECONDS
        )
        async with self.__uow:
            rows = await self.__uow.stations.read_many(
                org_id=org_id, field_id=field_id
            )
            return [
                StationOnFieldSchema(
                    hardware_id=r.hardware_id,
                    name=r.name,
                    latitude=r.latitude,
                    longitude=r.longitude,
                    last_seen_at=r.last_seen_at,
                    online=r.last_seen_at is not None and r.last_seen_at >= threshold,
                )
                for r in rows
            ]

    async def list_sensor_ids(
        self, hardware_id: int, org_id: uuid.UUID
    ) -> list[int]:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            return await self.__uow.sensor_data.list_sensor_ids(hardware_id)

    async def get_last_station_data(
        self, hardware_id: int, org_id: uuid.UUID
    ) -> StationDataReadSchema:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            row = await self.__uow.station_data.read_last(station_id=hardware_id)
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Station data for {hardware_id} not found.",
                )
            return StationDataReadSchema.model_validate(row, from_attributes=True)

    async def get_last_sensor_data(
        self, hardware_id: int, sensor_id: int, org_id: uuid.UUID
    ) -> SensorDataReadSchema:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            row = await self.__uow.sensor_data.read_last(
                station_id=hardware_id, sensor_id=sensor_id
            )
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sensor {sensor_id} data for station {hardware_id} not found.",
                )
            return SensorDataReadSchema.model_validate(row, from_attributes=True)

    async def get_station_history(
        self,
        hardware_id: int,
        date_from: datetime,
        date_to: datetime,
        org_id: uuid.UUID,
    ) -> list[StationDataReadSchema]:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            rows = await self.__uow.station_data.read_range(
                date_from=date_from, date_to=date_to, station_id=hardware_id
            )
            return [
                StationDataReadSchema.model_validate(r, from_attributes=True)
                for r in rows
            ]

    async def get_sensor_history(
        self,
        hardware_id: int,
        sensor_id: int,
        date_from: datetime,
        date_to: datetime,
        org_id: uuid.UUID,
    ) -> list[SensorDataReadSchema]:
        async with self.__uow:
            station = await self.__uow.stations.read(hardware_id=hardware_id)
            self._ensure_owner(station, org_id)
            rows = await self.__uow.sensor_data.read_range(
                date_from=date_from,
                date_to=date_to,
                station_id=hardware_id,
                sensor_id=sensor_id,
            )
            return [
                SensorDataReadSchema.model_validate(r, from_attributes=True)
                for r in rows
            ]

    @staticmethod
    def _ensure_owner(station, org_id: uuid.UUID) -> None:
        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Station not found",
            )
        if station.org_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Station does not belong to your organization",
            )
