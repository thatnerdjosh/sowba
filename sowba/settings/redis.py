from pydantic import RedisDsn
from pydantic import BaseModel


class RedisSettings(BaseModel):
    ...


class RedisConf(BaseModel):
    dsn: RedisDsn
    settings: RedisSettings
