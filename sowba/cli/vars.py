from contextvars import ContextVar
from sowba.settings.app import AppSettings
from sowba.settings.service import ServiceConf


config_file_var: ContextVar[str] = ContextVar("config_file_var")
settings_var: ContextVar[AppSettings] = ContextVar(
    "settings_var", default=None
)
service_name_var: ContextVar[str] = ContextVar("service_name_var")
