"""
export SOWBA_ENV_ADMIN_USER_PASSWORD="ChangeMe"
export SOWBA_ENV_SECURITY_SECRET_KEY="$(openssl rand -hex 32)"

sowba create [name] --storage=rocksdb --auth
sowba run [name] --storage=rocksdb
"""
import os
import sys
from pathlib import Path

import typer
import devtools
from pydantic import ValidationError

from sowba.registry import get as get_registry
from sowba.registry import add as add_registry
from sowba.core import path
from sowba.cli import config, service, auth
from sowba.settings.model import StorageName, ServiceStatus

from sowba.cli.utils import (
    create_app,
    load_settings,
    make_service_storage,
    make_service,
    make_app,
    run_app,
    load_service_endpoints,
    load_sevcurity,
)


sys.path.append(str(path.cwd()))

app = typer.Typer()
app.add_typer(config.app, name="config")
app.add_typer(service.app, name="service")
app.add_typer(auth.app, name="auth")


@app.callback()
def app_callback(
    ctx: typer.Context,
    config_file: Path = typer.Option("./config.json", "--config-file"),
):
    if ctx.invoked_subcommand == "create":
        typer.echo("Creating new project")
        return

    if not config_file.exists():
        typer.echo(f"Config file [{config_file}] not found.")
        raise typer.Abort()

    try:
        add_registry.app_settings(load_settings(config_file))
    except ValidationError as err:
        typer.echo(f"Error loading [{config_file}].")
        print(err)
        raise typer.Abort()

    typer.echo(f"Running project on: {config_file}")


@app.command()
def create(
    name: str,
    output: Path = typer.Option(Path("./")),
    storage: StorageName = typer.Option(StorageName.rocksdb),
    auth: bool = typer.Option(False),
):
    template = "default"
    if auth:
        template = "auth"
    try:
        create_app(name, output=output, storage=storage, template=template)
    except Exception as err:
        typer.echo(f"Eroor creating {name}: {err}")
        raise typer.Abort()
    typer.echo(f"name: {name}")
    typer.echo(f"storage: {storage}")
    typer.echo(f"path: {path.cwd()}/{name}")
    typer.echo("DONE!")


@app.command()
def run(storage: StorageName = typer.Option(None, "--settings-storage")):
    settings = get_registry.app_settings()
    typer.echo(f"app: {settings.name}")
    typer.echo(f"storage: {storage}")

    if storage is not None:
        for i, _ in enumerate(settings.services):
            settings.services[i].storage.connector = storage

    app = make_app(settings)
    if getattr(settings, "auth", None):
        load_sevcurity(app)

    for srv in settings.services:
        if srv.status == ServiceStatus.disable:
            continue
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
    devtools.debug(settings.asgi)
    run_app(app, settings)


if __name__ == "__main__":
    app()
