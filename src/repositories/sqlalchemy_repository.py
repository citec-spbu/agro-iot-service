from datetime import datetime
from typing import Generic, Type

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import ModelType
from src.repositories.base import AbstractRepository
from src.repositories.exceptions import DBIntegrityError


class SQLAlchemyRepository(AbstractRepository, Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.session = session
        self.model = model

    async def create(self, data: dict) -> ModelType:
        try:
            res = await self.session.execute(
                insert(self.model)
                .values(**data)
                .returning(self.model)
            )
            return res.scalar_one()
        except IntegrityError:
            raise DBIntegrityError(self.model.__name__)
            
    async def create_many(self, data: list[dict]) -> list[dict]:
        try:
            await self.session.execute(
                insert(self.model)
                .values(data)
            )
        except IntegrityError:
            raise DBIntegrityError(self.model.__name__)
        return data
            
    async def read(self, **filters) -> ModelType | None:
        res = await self.session.execute(
            select(self.model)
            .filter_by(**filters)
        )
        res_scalar = res.scalar_one_or_none()
        return res_scalar

    async def read_last(self, **filters) -> ModelType | None:
        res = await self.session.execute(
            select(self.model)
            .filter_by(**filters)
            .order_by(self.model.date_time.desc())
        )
        return res.scalars().first()

    async def read_all(self) -> list[ModelType]:
        res = await self.session.execute(
            select(self.model)
        )
        return res.scalars().all()

    async def read_many(self, **filters) -> list[ModelType]:
        res = await self.session.execute(
            select(self.model)
            .filter_by(**filters)
        )
        return res.scalars().all()

    async def read_range(
        self, date_from: datetime, date_to: datetime, **filters
    ) -> list[ModelType]:
        res = await self.session.execute(
            select(self.model)
            .filter_by(**filters)
            .where(self.model.date_time >= date_from)
            .where(self.model.date_time <= date_to)
            .order_by(self.model.date_time.asc())
        )
        return res.scalars().all()

    async def upsert(
        self,
        data_on_insert: dict,
        data_on_update: dict,
        index_elements: list[str]
    ) -> None:
        await self.session.execute(
            insert(self.model)
            .values(**data_on_insert)
            .on_conflict_do_update(
                index_elements=index_elements, set_={**data_on_update}
            )
        )

    async def delete(self, **filters) -> None:
        await self.session.execute(
            delete(self.model)
            .filter_by(**filters)
        )
