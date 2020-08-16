from abc import ABC
from abc import abstractmethod
from pydantic import BaseModel
from typing import Callable


class StorageInterface(ABC):
    @abstractmethod
    def configure(self, *args, **kwargs):
        ...

    @abstractmethod
    def settings(self, *args, **kwargs):
        ...

    @abstractmethod
    def setup(self, *args, **kwargs):
        ...


class BaseStorage(StorageInterface):

    default_setting: dict = {}

    def configure(
        self,
        model: BaseModel,
        /,
        dbname=None,
        deserialize: Callable[[bytes, BaseModel], BaseModel] = None,
        serialize: Callable[[BaseModel, BaseModel], bytes] = None,
        validate: Callable[[BaseModel, BaseModel], bool] = None,
    ):
        self.model = model
        self.dbname = dbname or str.lower(model.__name__)
        self.deserialize = deserialize
        self.serialize = serialize
        self.validate = validate

    def settings(self, **kwargs):
        self._settings = {**self.default_settings, **kwargs}

    def get_settings(self):
        return getattr(self, "_settings", {})

    def setup(self):
        ...


if __name__ == "__main__":
    b = BaseStorage()
