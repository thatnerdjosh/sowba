from typing import List
from typing import Optional
from pydantic import PyObject
from pydantic import BaseModel
from sowba.storage import StorageName


class RocksdbSettings(BaseModel):
    rocksdb: str


class MongodbSettings(BaseModel):
    ...


class CouchbaseSettings(BaseModel):
    ...


class ConnectorConfig(BaseModel):
    deserialize: Optional[PyObject] = "sowba.storage.rocks_db.deserialize"
    serialize: Optional[PyObject] = "sowba.storage.rocks_db.serialize"
    validator: Optional[PyObject] = "sowba.storage.rocks_db.validator"


class ConnectorConf(BaseModel):
    connector: StorageName = StorageName.rocksdb
    connector_cls: Optional[PyObject] = None
    configuration: ConnectorConfig
    settings: dict


class StoragesConf(BaseModel):
    default: StorageName
    connectors: List[ConnectorConf]
