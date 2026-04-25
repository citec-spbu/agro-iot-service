from src.database.helper import db_helper
from src.repositories.iot_data import SensorDataRepository, StationDataRepository
from src.repositories.stations import StationsRepository
from src.repositories.uow.base import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self):
        self.session_factory = db_helper.get_session_factory()

    async def __aenter__(self):
        self.session = self.session_factory()

        self.stations = StationsRepository(self.session)
        self.station_data = StationDataRepository(self.session)
        self.sensor_data = SensorDataRepository(self.session)

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
