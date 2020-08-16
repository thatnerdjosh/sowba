from abc import ABC
from enum import Enum
from typing import Callable
from pydantic import BaseModel
from abc import abstractmethod


class StorageName(str, Enum):
    rocksdb: str = "rocksdb"
    mongodb: str = "mongodb"
    couchbase: str = "couchbase"


class StorageInterface(ABC):
    @abstractmethod
    def configure(self, **kwargs):
        ...

    @abstractmethod
    def settings(self, **kwargs):
        ...

    @abstractmethod
    def setup(self, *args, **kwargs):
        ...

    @abstractmethod
    def close(self, *args, **kwargs):
        ...

    @abstractmethod
    def store(self, *args, **kwargs):
        ...

    @abstractmethod
    def get(self, *args, **kwargs):
        ...

    def getmany(self, *args, **kwargs):
        ...

    @abstractmethod
    def update(self, *args, **kwargs):
        ...

    @abstractmethod
    def delete(self, *args, **kwargs):
        ...

    @abstractmethod
    def find(self, *args, **kwargs):
        ...

    @abstractmethod
    def search(self, *args, **kwargs):
        ...


class BaseStorage(StorageInterface):
    default_settings: dict = {}

    def configure(
        self,
        model: BaseModel,
        /,
        dbname=None,
        deserialize: Callable[[bytes, BaseModel], BaseModel] = None,
        serialize: Callable[[BaseModel, BaseModel], bytes] = None,
        validator: Callable[[BaseModel, BaseModel], bool] = None,
    ):
        self.model = model
        self.dbname = dbname or str.lower(model.__name__)
        self.deserialize = deserialize
        self.serialize = serialize
        self.validator = validator

    def settings(self, **kwargs):
        self._settings = {**self.default_settings, **kwargs}

    def getsettings(self):
        return getattr(self, "_settings", self.default_settings)

    def setup(self, *args, **kwargs):
        ...

    def close(self, *args, **kwargs):
        ...

    def store(self, *args, **kwargs):
        ...

    def get(self, arg):
        ...

    def getmany(self, *args):
        ...

    def update(self, *args, **kwargs):
        ...

    def delete(self, *args, **kwargs):
        ...

    def find(self, *args, **kwargs):
        ...

    def search(self, *args, **kwargs):
        ...
