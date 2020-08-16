from enum import Enum
from typing import Union
from typing import List
from pydantic import BaseModel


class StreamType(str, Enum):
    kafka: str = "kafka"


class KafkaConsumerConf(BaseModel):
    ...


class KafkaProducerConf(BaseModel):
    ...


class KafkaSettings(BaseModel):
    bootstrap_servers: List[str]
    consumer: KafkaConsumerConf
    producer: KafkaProducerConf


class StreamConf(BaseModel):
    type: StreamType
    settings: KafkaSettings
