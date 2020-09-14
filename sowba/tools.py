import asyncio
import importlib
import json
from datetime import datetime, timedelta

import jwt
import typer
import uvicorn
from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import EmailStr, FilePath
from pydantic.parse import load_file

from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

# from sowba.cli.vars import config_file_var
from sowba.core import path
from sowba.core.application import SApp, SService, SServiceRouter
from sowba.core.model import SBaseModel
from sowba.settings import get as get_app_settings
from sowba.registry import service as service_registry
from sowba.registry import storage as storage_registry
from sowba.settings.model import AppSettings, StorageName
from sowba.settings.plugin import PluginSettings
from sowba.settings.model import Service as ServiceConf, ServiceStatus
from sowba.settings.model import Connector as ConnectorConf, ConnectorConfig
from sowba.storage import BaseStorage


from sowba.cli.plugin import cache as cache_plugin
from sowba.cli.plugin import kafka as kafka_plugin
from sowba.cli.plugin import users as users_plugin


def isiterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def create_app(
    name, /, output="./", storage: StorageName = "rocksdb", template="default"
):
    try:
        cookiecutter(
            f"{path.template.app}/{template}",
            output_dir=output,
            no_input=True,
            extra_context={"app": name, "storage": storage.value},
        )
    except OutputDirExistsException:
        typer.echo(f"Eroor: App {name} alredy exist!")
        raise typer.Abort()


def add_service(app, service):
    try:
        cookiecutter(
            f"{path.template.service}/folder",
            output_dir=f"{path.cwd()}/{app}/services",
            no_input=True,
            extra_context={"service": service},
        )
    except OutputDirExistsException:
        typer.echo(f"Eroor: Service {service} alredy exist!")
        raise typer.Abort()


def add_plugin(name: str, settings: AppSettings) -> AppSettings:
    ...
    # plugin = {
    #     "users": {
    #         "admin": {"username": "admin", "email": "admin@sowba.com"},
    #         "security": {
    #             "algorithm": "HS256",
    #             "access_token_expire_minutes": 30,
    #             "auth_path": "/token",
    #         },
    #         "model": "sowba.core.model.SBaseUserModel",
    #     },
    #     "cache": {
    #         "size": 100,
    #         "redis": {"dsn": "redis://keydb.sowba.io/0", "settings": {}},
    #     },
    #     "kafka": {
    #         "bootstrap_servers": [
    #             "kafka1.sowba.io:9092",
    #             "kafka2.sowba.io:9092",
    #             "kafka3.sowba.io:9092",
    #         ],
    #         "consumer": {},
    #         "producer": {},
    #     },
    # }[name]
    # plugins = settings.get("plugins", {})
    # plugins[name] = plugin
    # settings["plugins"] = plugins
    # typer.echo(f"Updating plugin: {name}")
    # print(
    #     json.dumps(settings, indent=4), file=open(config_file_var.get(), "wt")
    # )
    # return settings


def update_service_status(name: str, status: ServiceStatus):
    settings = get_app_settings()
    assert settings, "Settings lookup error."
    conf = load_file(settings.file)
    for i, srv in enumerate(conf.get("services", [])):
        if srv["name"] == name:
            srv["status"] = status
            conf["services"][i] = srv
            print(json.dumps(conf, indent=4), file=open(settings.file, "wt"))
            break
    else:
        typer.echo(f"Eroor: service {name} not found")


def register_service_storage(
    name: str, settings: AppSettings, connector: StorageName
):
    storage = get_storage(name, settings, connector=connector)
    storage_registry.register(name, storage)


def register_service_route(name, settings: AppSettings):
    storage = storage_registry.get(name)
    srv = get_service_conf(name, settings)
    if srv is None:
        typer.echo(f"{name}: Service not found.")
        raise typer.Abort()
    if srv.status != ServiceStatus.enable:
        typer.echo(f"{name}: Service disable.")
        raise typer.Abort()
    router = make_service_router(name, storage, settings)
    service_registry.register_router(name, router)
    importlib.import_module(f"{settings.name}.services.{name}.endpoints")
    return router


def make_service_router(
    name, storage: BaseStorage, settings: AppSettings
) -> SServiceRouter:
    router = SServiceRouter(
        servicename=name, servicestorage=storage, app_settings=settings
    )
    router.conf.storage.model = SService(router, name=name)(
        router.conf.storage.model
    )
    return router


def run_all_services(settings: AppSettings, server=uvicorn.run):
    # app = SApp(settings=settings)
    # for srv in settings.services:
    #     router = make_service_router(srv.name, settings)
    #     register_service_router(srv.name, router)
    #     app.include_router(
    #         router,
    #         tags=[f"{settings.name}@{srv.name}"],
    #         prefix=f"{settings.name}/{srv.name}",
    #         responses={
    #             404: {
    #                 "service": f"{settings.name}/{srv.name}",
    #                 "error": "NOT_FOUND",
    #             }
    #         },
    #     )
    # return server(app, **settings.asgi.dict())
    ...


def run_service(name, settings: AppSettings, server=uvicorn.run):
    # app = SApp(settings=settings)
    # srv = get_service_conf(name, settings)
    # assert srv, f"Service {name}: NOT_FOUND"
    # router = make_service_router(name, settings)
    # register_service_router(name, router)
    # app.include_router(
    #     router,
    #     tags=[f"{settings.name}@{name}"],
    #     prefix=f"{settings.name}/{name}",
    #     responses={
    #         404: {"service": f"{settings.name}/{name}", "error": "NOT_FOUND"}
    #     },
    # )
    # return server(app, **settings.asgi.dict())
    ...


def load_pugin(name: str, app: SApp, settings: AppSettings):
    {
        "users": users_plugin.load,
        "cache": cache_plugin.load,
        "kafka": kafka_plugin.load,
    }[name](app, settings)


def load_pugins(app: SApp, settings: AppSettings):
    plugins = getattr(settings, "plugins") or PluginSettings()
    for plugin_name, plugin in vars(plugins).items():
        if plugin:
            load_pugin(plugin_name, app, settings)


def start_service(
    name: str, settings: AppSettings, server=uvicorn.run,
):
    router = service_registry.get_router(name)
    app = SApp(settings=settings)
    app_registry.register_app(app)
    app.configure(settings)
    load_pugins(app, settings)
    app.include_router(
        router,
        tags=[router.tag],
        prefix=router.prefix,
        responses={
            404: {"service": f"{settings.name}/{name}", "error": "NOT_FOUND"}
        },
    )
    asgi = settings.asgi.dict()
    asgi["host"] = str(asgi["host"])
    return server(app, **asgi)


def start_services(settings: AppSettings, server=uvicorn.run):
    routers = []
    for srv in settings.services:
        if srv.status != ServiceStatus.enable:
            continue
        router = service_registry.get_router(srv.name)
        routers.append(router)

    app = SApp(settings=settings)
    app.configure(settings)
    load_pugins(app, settings)
    for router in routers:
        app.include_router(
            router,
            tags=[router.tag],
            prefix=router.prefix,
            responses={
                404: {
                    "service": f"{settings.name}/{router.conf.name}",
                    "error": "NOT_FOUND",
                }
            },
        )
    asgi = settings.asgi.dict()
    asgi["host"] = str(asgi["host"])
    return server(app, **asgi)


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "1fe11dfa433ce37f4abe64c28cd70d2a27f9a6244df7394de0b2826fafd03d86"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def email_is_available(email):
    ...


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(db, email: EmailStr):
    try:
        if asyncio.iscoroutinefunction(db.get):
            user = await db.get(email)
        else:
            user = db.get(email)
    except HTTPException:
        return
    return user["item"]


def create_access_token(*, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def principals_validator(principals):
    for principal in principals:
        if len(principal.split(":")) != 2:
            raise HTTPException(
                status_code=412, detail=f"Invalid pricipal format: {principal}"
            )
    return principals


def get_service_conf(name: str, settings: AppSettings) -> ServiceConf:
    for service in settings.services:
        if service.name == name:
            return service
    return


def get_service_connector_name(
    service: ServiceConf, settings: AppSettings
) -> StorageName:
    return service.storage.connector or settings.storages.default


def load_settings(configfile: FilePath) -> AppSettings:
    return AppSettings(file=configfile, **load_file(configfile))


def get_app_connector_conf(
    connector: StorageName, settings: AppSettings
) -> ConnectorConf:
    for conf in settings.storages.connectors:
        if conf.connector == connector:
            return conf
    return


def make_storage(
    model: SBaseModel,
    connector_cls: BaseStorage,
    storage_configs: ConnectorConfig = None,
    storage_settings: dict = None,
) -> BaseStorage:

    storage_configs = storage_configs or ConnectorConfig()
    storage_settings = storage_settings or dict()
    assert issubclass(
        connector_cls, BaseStorage
    ), f"<{connector_cls}> invalid connector class."
    storage = connector_cls()
    storage.configure(model, **storage_configs.dict())
    storage.settings(**storage_settings)
    # storage.setup()
    return storage


def get_storage(
    servicename: str, settings: AppSettings, /, connector: StorageName = None
) -> BaseStorage:

    service = get_service_conf(servicename, settings)
    assert service, f"Service <{servicename}> not found in {settings.file}."
    assert (
        service.status == ServiceStatus.enable
    ), f"Service <{servicename}> must be enabled."
    connector_name = connector or get_service_connector_name(service, settings)
    connector_conf = get_app_connector_conf(connector_name, settings)
    assert connector_conf, f"No connector found for Service: <{servicename}>"
    return make_storage(
        service.storage.model,
        connector_conf.connector_cls,
        storage_configs=connector_conf.configuration,
        storage_settings=connector_conf.settings,
    )
