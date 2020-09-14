"""
sowba --admin-passwd=... --secret-key=...  config ls
sowba --admin-passwd=... --secret-key=...  config ls name
sowba --admin-passwd=... --secret-key=...  config ls admin_user
sowba --admin-passwd=... --secret-key=...  config ls services
sowba --admin-passwd=... --secret-key=...  config ls settings
sowba --admin-passwd=... --secret-key=...  config ls security
sowba --admin-passwd=... --secret-key=...  config ls asgi
sowba --admin-passwd=... --secret-key=...  config ls cors
"""
from enum import Enum

import devtools
import typer
from sowba.registry import get as get_registry

app = typer.Typer()


class LsValues(str, Enum):
    name: str = "name"
    asgi: str = "asgi"
    cors: str = "cors"
    auth: str = "auth"
    services: str = "services"
    storages: str = "storages"


@app.command()
def ls(config_name: LsValues = typer.Argument(None)):

    settings = get_registry.app_settings()

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
