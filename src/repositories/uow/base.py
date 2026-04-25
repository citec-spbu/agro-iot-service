from abc import ABC, abstractmethod
from typing import Type

from src.repositories.iot_data import SensorDataRepository, StationDataRepository
from src.repositories.stations import StationsRepository


class UnitOfWork(ABC):
    stations: Type[StationsRepository]
    station_data: Type[StationDataRepository]
    sensor_data: Type[SensorDataRepository]

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...
