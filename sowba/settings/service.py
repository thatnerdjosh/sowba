from enum import Enum
from typing import Dict
from typing import Union
from typing import Optional
from pydantic import PyObject
from pydantic import BaseModel
from sowba.storage import StorageName
from sowba.settings.stream import KafkaConsumerConf
from sowba.settings.stream import KafkaProducerConf


class ServiceSettings(BaseModel):
    storage: StorageName = StorageName.rocksdb
    consumer: Optional[KafkaConsumerConf]
    producer: Optional[KafkaProducerConf]


class ServiceStatus(str, Enum):
    enable: str = "enable"
    disable: str = "disable"


class ServiceConf(BaseModel):
    name: str
    model: Union[PyObject, Dict]
    status: ServiceStatus = ServiceStatus.enable
    settings: Optional[ServiceSettings]
