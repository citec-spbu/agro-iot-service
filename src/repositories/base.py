from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, *args, **kwargs):
        ...

    @abstractmethod
    async def read(self, *args, **kwargs):
        ...

    @abstractmethod
    async def read_all(self, *args, **kwargs):
        ...

    @abstractmethod
    async def read_many(self, *args, **kwargs):
        ...

    @abstractmethod
    async def upsert(self, *args, **kwargs):
        ...

    @abstractmethod
    async def delete(self, *args, **kwargs):
        ...
