import json
import typer
import uvicorn
import importlib
from sowba.core import path
from sowba.settings.model import StorageName
from sowba.storage import BaseStorage
from sowba.settings.model import AppSettings
from sowba.settings.model import ConnectorConfig
from sowba.settings.model import ServiceStatus

from sowba.core import SApp
from sowba.core.decorator import api
from sowba.core import SServiceRouter

from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException


import pathlib
from typing import Dict
from pydantic import FilePath
from pydantic.parse import load_file

from sowba.registry import add as add_registry
from sowba.core.model import SBaseModel


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


def create_service(app, service):
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

def make_app(settings: AppSettings) -> SApp:
    app = SApp(settings=settings)
    app.configure(settings)
    return app


def run_app(app: SApp, settings: AppSettings, server=uvicorn.run):
    asgi = settings.asgi.dict()
    asgi["host"] = str(asgi["host"])
    return server(app, **asgi)


def make_service_storage(service: str, settings: AppSettings) -> BaseStorage:
    srv = None
    for srv in settings.services:
        if srv.name == service:
            break
    else:
        raise Exception(f"Service: {service} lookup error")

    conn = getattr(srv, "storage", None) or settings.storages.default
    storage_settings = None
    for storage_settings in settings.storages.connectors:
        if storage_settings.name == conn.connector:
            break
    else:
        raise Exception(f"Service storage: {conn.connector} lookup error")

    storage = storage_settings.factory()
    storage.configure(
        srv.storage.model,
        **getattr(storage_settings, "configuration", ConnectorConfig()).dict(),
    )
    storage.settings(**getattr(storage_settings, "settings", dict()))
    return storage


def make_service(name: str, storage: BaseStorage, settings: AppSettings):
    router = SServiceRouter(storage=storage)
    router.storage.model = api(router, storage, name=name)(
        router.storage.model
    )
    return router


def load_service_endpoints(service: str, settings: AppSettings):
    importlib.import_module(f"{settings.name}.services.{service}.endpoints")


def update_service_status(
    name: str, status: ServiceStatus, settings: AppSettings
):
    conf = load_file(settings.file)
    for i, srv in enumerate(conf.get("services", [])):
        if srv["name"] == name:
            srv["status"] = status
            conf["services"][i] = srv
            print(json.dumps(conf, indent=4), file=open(settings.file, "wt"))
            break
    else:
        typer.echo(f"Eroor: service {name} not found")


def load_raw_settings(
    config: FilePath = pathlib.Path("./config.json"),
) -> Dict:
    return {"file": config, **load_file(config)}


def load_settings(
    config: FilePath = pathlib.Path("./config.json"),
) -> AppSettings:
    return AppSettings(**load_raw_settings(config))


def load_sevcurity(app: SApp):
    return

def bootstrap_app(
    settings: AppSettings,
    storage: StorageName = None,
) -> SApp:
    app = make_app(settings)
    if getattr(settings, "auth", None):
        load_sevcurity(app)

    for i, srv in enumerate(settings.services):
        if srv.status == ServiceStatus.disable:
            continue
        if storage is not None:
            settings.services[i].storage.connector = storage
        storage = make_service_storage(srv.name, settings)
        add_registry.storage(srv.name, storage)
        router = make_service(srv.name, storage, settings)
        add_registry.service(srv.name, router)
        load_service_endpoints(srv.name, settings)
        app.include_router(
            router,
            tags=[f"{settings.name}@{srv.name}"],
            prefix=f"/{settings.name}/{srv.name}",
            responses={
                404: {
                    "service": f"{settings.name}/{srv.name}",
                    "error": "NOT_FOUND",
                }
            },
        )
    add_registry.app_settings(settings)
    return app
