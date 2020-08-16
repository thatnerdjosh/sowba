"""
sowba service [name] consumer run --config config.jon
"""
import os
import typer
import devtools
from enum import Enum
from .vars import config_file_var
from pydantic import ValidationError
from sowba.settings.utils import load_settings

app = typer.Typer()


class LsValues(str, Enum):
    name: str = "name"
    admin_user: str = "admin_user"
    services: str = "services"
    settings: str = "settings"
    security: str = "security"
    asgi: str = "asgi"
    cors: str = "cors"


@app.command()
def ls(
    config_name: LsValues = typer.Argument(None),
    admin_password: str = typer.Option(None, "--admin-passwd"),
    secret_key: str = typer.Option(None, "--secret-key"),
):
    config_file = config_file_var.get()

    if admin_password:
        os.environ["SOWBA_ENV_ADMIN_USER_PASSWORD"] = admin_password

    if secret_key:
        os.environ["SOWBA_ENV_SECURITY_SECRET_KEY"] = secret_key

    try:
        settings = load_settings(config_file)
    except ValidationError as err:
        typer.echo(f"Error loading [{config_file}].")
        print(err)
        raise typer.Abort()

    if config_name is None:
        devtools.debug(settings)
    else:
        config = vars(settings).get(config_name)
        if config is None:
            typer.echo(f"Invalid config: {config_name}")
            raise typer.Abort()
        devtools.debug(config)


if __name__ == "__main__":
    app()
