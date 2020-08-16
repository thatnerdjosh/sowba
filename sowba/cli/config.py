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
import typer
import devtools
from enum import Enum
from .vars import settings_var

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
def ls(config_name: LsValues = typer.Argument(None)):

    settings = settings_var.get()

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
