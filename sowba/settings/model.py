from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    BaseSettings,
    EmailStr,
    Field,
    FilePath,
    IPvAnyAddress,
    PyObject,
    RedisDsn,
    SecretStr,
)


class StorageName(str, Enum):
    rocksdb: str = "rocksdb"
    mongodb: str = "mongodb"
    couchbase: str = "couchbase"


class LogLevel(str, Enum):
    info: str = "info"
    error: str = "error"
    debug: str = "debug"
    warning: str = "warning"
    critical: str = "critical"


class Asgi(BaseModel):
    host: IPvAnyAddress
    port: int
    debug: bool = False
    reload: bool = False
    timeout_keep_alive: int = 20
    proxy_headers: bool = True
    log_level: LogLevel = LogLevel.info


class Cors(BaseModel):
    max_age: int = 600
    allow_credentials: bool = False
    allow_origins: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    allow_methods: List[str] = ["*"]
    expose_headers: List[Any] = Field(default_factory=list)


class JwtAlgorithm(str, Enum):
    hs256: str = "HS256"
    rs256: str = "RS256"


class AdminUser(BaseSettings):
    """
    export SOWBA_ENV_ADMIN_USER_PASSWORD="ChangeMe"
    """

    username: str
    email: EmailStr
    password: SecretStr = Field(
        "ChangeMe", env="SOWBA_ENV_ADMIN_USER_PASSWORD"
    )


class Security(BaseSettings):
    """
    export SOWBA_ENV_SECURITY_SECRET_KEY="$(openssl rand -hex 32)"
    """

    secret_key: str = Field("ChangeMe", env="SOWBA_ENV_SECURITY_SECRET_KEY")
    auth_path: str
    algorithm: JwtAlgorithm
    access_token_expire_minutes: int


class Auth(BaseSettings):
    admin: AdminUser
    security: Security


class Redis(BaseModel):
    dsn: RedisDsn
    settings: Dict = Field(default_factory=dict)


class ServiceStatus(str, Enum):
    enable: str = "enable"
    disable: str = "disable"


class ConnectorConfig(BaseModel):
    deserialize: Optional[PyObject] = "sowba.storage.rocks_db.deserialize"
    serialize: Optional[PyObject] = "sowba.storage.rocks_db.serialize"
    validator: Optional[PyObject] = "sowba.storage.rocks_db.validator"


class Connector(BaseModel):
    name: StorageName = StorageName.rocksdb
    factory: Optional[PyObject]
    configuration: Optional[ConnectorConfig]
    settings: Optional[dict]


class Storages(BaseModel):
    default: StorageName
    connectors: List[Connector]


class ServiceStorage(BaseModel):
    model: Union[PyObject, Dict]
    connector: Optional[StorageName] = StorageName.rocksdb


class Service(BaseModel):
    name: str
    status: ServiceStatus = ServiceStatus.enable
    storage: ServiceStorage
    settings: Optional[Dict]


class AppSettings(BaseSettings):
    name: str
    file: FilePath
    services: List[Service] = Field(default_factory=list)
    storages: Storages
    auth: Optional[Auth]
    asgi: Asgi
    cors: Cors

    class Config:
        env_prefix = "SOWBA_ENV_"
