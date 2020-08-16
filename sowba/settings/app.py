from enum import Enum
from typing import Any
from typing import List
from pydantic import Field
from pydantic import FilePath
from pydantic import BaseModel
from pydantic import BaseSettings

from pydantic import SecretStr
from pydantic import EmailStr
from pydantic import IPvAnyAddress

from sowba.settings.service import ServiceConf
from sowba.settings.stream import StreamConf
from sowba.settings.redis import RedisConf
from sowba.settings.storage import StoragesConf


class LogLevelConf(str, Enum):
    info: str = "info"
    error: str = "error"
    debug: str = "debug"
    warning: str = "warning"
    critical: str = "critical"


class JwtAlgorithmConf(str, Enum):
    hs256: str = "HS256"
    rs256: str = "RS256"


class AdminUserConf(BaseSettings):
    """
    export SOWBA_ENV_ADMIN_USER_PASSWORD="ChangeMe"
    """

    username: str
    email: EmailStr
    password: SecretStr = Field(..., env="SOWBA_ENV_ADMIN_USER_PASSWORD")


class SettingsConf(BaseModel):
    storages: StoragesConf
    redis: RedisConf
    stream: StreamConf


class SecurityConf(BaseSettings):
    """
    export SOWBA_ENV_SECURITY_SECRET_KEY="$(openssl rand -hex 32)"
    """

    secret_key: str = Field(..., env="SOWBA_ENV_SECURITY_SECRET_KEY")
    algorithm: JwtAlgorithmConf
    access_token_expire_minutes: int


class AsgiConf(BaseModel):
    host: IPvAnyAddress
    port: int
    debug: bool = False
    reload: bool = False
    timeout_keep_alive: int = 20
    proxy_headers: bool = True
    log_level: LogLevelConf = LogLevelConf.info


class CorsConf(BaseModel):
    max_age: int = 600
    allow_credentials: bool = False
    allow_origins: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    allow_methods: List[str] = ["*"]
    expose_headers: List[Any] = Field(default_factory=list)


class AppSettings(BaseSettings):
    name: str
    file: FilePath
    admin_user: AdminUserConf
    services: List[ServiceConf] = Field(default_factory=list)
    settings: SettingsConf
    security: SecurityConf
    asgi: AsgiConf
    cors: CorsConf

    class Config:
        env_prefix = "SOWBA_ENV_"
