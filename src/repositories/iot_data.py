import uuid

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.iot_data import SensorData, StationData
from src.repositories.sqlalchemy_repository import SQLAlchemyRepository


class StationDataRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(StationData, session)


class SensorDataRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SensorData, session)

    async def list_sensor_ids(self, field_id: uuid.UUID) -> list[int]:
        res = await self.session.execute(
            select(distinct(SensorData.sensor_id))
            .where(SensorData.field_id == field_id)
            .order_by(SensorData.sensor_id)
        )
        return list(res.scalars().all())
