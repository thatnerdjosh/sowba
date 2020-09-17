"""
sowba service [name] ls
sowba service [name] enable
sowba service [name] disable

sowba service add [name] --settings-storage=rocksdb
sowba service run [name] --settings-storage=rocksdb
"""
import json

import devtools
import typer
from typing import List
from pydantic import PyObject, PyObjectError
from sowba.cli.utils import (
    bootstrap_app,
    load_raw_settings,
    create_service,
    update_service_status,
    make_service_storage,
    make_service,
    make_app,
    run_app,
    load_service_endpoints,
)

from sowba.settings.model import ServiceStatus
from sowba.settings.model import StorageName
from sowba.registry import get as get_registry
from sowba.registry import add as add_registry


app = typer.Typer()


@app.command()
def add(
    name: str = typer.Argument(...),
    model: str = typer.Option(None),
    storage: StorageName = typer.Option(
        StorageName.rocksdb, "--settings-storage"
    ),
):
    settings = get_registry.app_settings()

    if model is not None:
        try:
            PyObject.validate(model)
        except PyObjectError as err:
            typer.echo(f"Error model: {err}")
            raise typer.Abort()

    for srv in settings.services:
        if srv.name == name:
            typer.echo(f"Error: duplicated service name: {name}.")
            raise typer.Abort()

    conf = load_raw_settings(settings.file)
    conf["services"].append(
        {
            "name": name,
            "status": "enable",
            "storage": {
                "model": model
                or f"{conf['name']}.services.{name}.model.{name.capitalize()}",
                "connector": storage,
            },
        }
    )
    typer.echo(f"Adding new service to [{settings.name}]:")
    typer.echo(f"name: {name}")
    typer.echo(f"-> apdating {settings.file}.")
    config_file = conf.pop("file")
    print(json.dumps(conf, indent=4), file=open(config_file, "wt"))
    typer.echo("-> adding service package")
    create_service(conf["name"], name)


@app.command()
def ls():
    ...
    # name = service_registry.get_name()
    # settings = app_registry.get_settings()
    # devtools.debug(settings)
    # typer.echo("-> Listing endpoint.")


@app.command()
def enable(name: str = typer.Argument(...)):
    settings = get_registry.app_settings()
    update_service_status(name, ServiceStatus.enable, settings)


@app.command()
def disable(name: str = typer.Argument(...)):
    settings = get_registry.app_settings()
    update_service_status(name, ServiceStatus.disable, settings)


@app.command()
def run(
    names: List[str],
    storage: StorageName = typer.Option(None, "--settings-storage"),
):
    settings = get_registry.app_settings()
    services = list(
        filter(lambda x: x[1].name in names, enumerate(settings.services))
    )

    bootstrap_app(settings, services, storage)
    app = get_registry.app()
    devtools.debug(settings.asgi)
    run_app(app, settings)


if __name__ == "__main__":
    app()
