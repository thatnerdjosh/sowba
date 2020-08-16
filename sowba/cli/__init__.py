"""
export SOWBA_ENV_ADMIN_USER_PASSWORD="ChangeMe"
export SOWBA_ENV_SECURITY_SECRET_KEY="$(openssl rand -hex 32)"

sowba create [name] --storage=rocksdb
sowba run [name] --storage=rocksdb
"""
import os
import sys
import typer
import devtools
from pathlib import Path
from sowba.core import path
from sowba.storage import StorageName

from pydantic import ValidationError
from sowba.settings.utils import load_settings

from sowba.cli import config
from sowba.cli import service
from sowba.cli import plugin
from sowba.cli.utils import create_app
from sowba.cli.vars import settings_var
from sowba.cli.vars import config_file_var


sys.path.append(str(path.cwd()))

app = typer.Typer()
app.add_typer(config.app, name="config")
app.add_typer(service.app, name="service")
app.add_typer(plugin.app, name="plugin")


@app.callback()
def app_callback(
    ctx: typer.Context,
    config_file: Path = typer.Option("./config.json", "--config-file"),
    admin_password: str = typer.Option(None, "--admin-passwd"),
    secret_key: str = typer.Option(None, "--secret-key"),
):
    if ctx.invoked_subcommand == "create":
        typer.echo("Creating new project")
        return

    if not config_file.exists():
        typer.echo(f"Config file [{config_file}] not found.")
        raise typer.Abort()

    if admin_password:
        os.environ["SOWBA_ENV_ADMIN_USER_PASSWORD"] = admin_password

    if secret_key:
        os.environ["SOWBA_ENV_SECURITY_SECRET_KEY"] = secret_key

    try:
        settings = load_settings(config_file)
        settings_var.set(settings)
    except ValidationError as err:
        typer.echo(f"Error loading [{config_file}].")
        print(err)
        raise typer.Abort()

    typer.echo(f"Running project on: {config_file}")
    config_file_var.set(config_file)


@app.command()
def create(
    name: str,
    output: Path = typer.Option(Path("./")),
    storage: StorageName = typer.Option("rocksdb"),
    template: str = typer.Option("default"),
):
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
def run(name: str, storage: StorageName = StorageName.rocksdb):
    settings = settings_var.get()
    typer.echo(f"storage: {storage}")
    devtools.debug(settings.asgi)


if __name__ == "__main__":
    app()
