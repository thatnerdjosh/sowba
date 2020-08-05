from abc import ABC, abstractmethod


class DBConnector(ABC):

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
    def update(self, *args, **kwargs):
        ...

    @abstractmethod
    def delete(self, *args, **kwargs):
        ...

    @abstractmethod
    def get(self, *args, **kwargs):
        ...

    @abstractmethod
    def find(self, *args, **kwargs):
        ...
