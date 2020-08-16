"""
sowba service [name] ls
sowba service [name] enable
sowba service [name] disable

sowba service [name] add --settings-storage=rocksdb \
    --model="examples.model.User"
sowba service [name] run --settings-storage=rocksdb \
    --model="examples.model.User"
"""
import json
import typer
import devtools
import importlib

from pydantic import PyObject
from pydantic import PyObjectError
from pydantic.parse import load_file

from sowba.settings.service import ServiceConf
from sowba.settings.service import ServiceStatus
from sowba.settings.service import ServiceSettings

from sowba.cli.vars import settings_var
from sowba.cli.vars import config_file_var
from sowba.cli.vars import service_name_var

from sowba.storage import StorageName
from sowba.storage.utils import get_service_conf
from sowba.core.utils import make_service_router
from sowba.core.utils import register_service_router
from sowba.core.utils import start_service


app = typer.Typer()


@app.callback(invoke_without_command=True)
def service_callback(ctx: typer.Context, name: str):
    typer.echo(f"Operating on service: {name}")
    service_name_var.set(name)


@app.command()
def add(
    model: str = typer.Option(...),
    storage: StorageName = typer.Option(
        StorageName.rocksdb, "--settings-storage"
    ),
):
    name = service_name_var.get()
    settings = settings_var.get()
    config_file = config_file_var.get()

    try:
        PyObject.validate(model)
    except PyObjectError as err:
        typer.echo(f"Error model: {err}")
        raise typer.Abort()

    for srv in settings.services:
        if srv.name == name:
            typer.echo(f"Error: duplicated service name: {name}.")
            raise typer.Abort()

    conf = load_file(config_file)
    conf["services"].append(
        {
            "name": name,
            "status": "enable",
            "model": model,
            "settings": {
                "storage": storage,
                "consumer": None,
                "producer": None,
            },
        }
    )
    typer.echo("-> Added new service.")
    print(json.dumps(conf, indent=4), file=open(settings.file, "wt"))


@app.command()
def ls():
    name = service_name_var.get()
    typer.echo("-> Listing endpoint.")


@app.command()
def enable():
    name = service_name_var.get()
    typer.echo("-> Enableing service.")


@app.command()
def disable():
    name = service_name_var.get()
    typer.echo("-> Disableing service")


@app.command()
def run(
    model: str = typer.Option(None),
    storage: StorageName = typer.Option(
        StorageName.rocksdb, "--settings-storage"
    ),
):
    name = service_name_var.get()
    settings = settings_var.get()
    srv = get_service_conf(name, settings)
    if srv is None:
        typer.echo(f"{name}: Service not found.")
        raise typer.Abort()
    if srv.status != ServiceStatus.enable:
        typer.echo(f"{name}: Service disable.")
        raise typer.Abort()
    router = make_service_router(name, settings)
    register_service_router(name, router)
    importlib.import_module(f"{settings.name}.services.{name}.endpoints")

    typer.echo("-> Running service")
    devtools.debug(srv)
    start_service(name, router, settings)


if __name__ == "__main__":
    app()
