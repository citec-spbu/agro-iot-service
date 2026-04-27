from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.stations import Station
from src.repositories.sqlalchemy_repository import SQLAlchemyRepository


class StationsRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Station, session)

    async def update_last_seen(self, hardware_id: int, last_seen_at) -> None:
        await self.session.execute(
            update(Station)
            .where(Station.hardware_id == hardware_id)
            .values(last_seen_at=last_seen_at)
        )
