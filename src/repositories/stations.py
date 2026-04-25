from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
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

    async def upsert_coords(
        self, hardware_id: int, latitude: float, longitude: float
    ) -> None:
        await self.session.execute(
            insert(Station)
            .values(
                hardware_id=hardware_id,
                latitude=latitude,
                longitude=longitude,
            )
            .on_conflict_do_update(
                index_elements=["hardware_id"],
                set_={"latitude": latitude, "longitude": longitude},
            )
        )
