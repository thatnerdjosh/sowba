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
from enum import Enum
from typing import List
from pydantic import PyObject, PyObjectError, EmailStr, EmailError
from sowba.cli.utils import (
    load_raw_settings,
    create_service,
    update_service_status,
    make_service_storage,
    make_service,
    make_app,
    run_app,
    load_service_endpoints,
)
from sowba.core import path
from sowba.settings.model import ConnectorConfig
from sowba.settings.model import ServiceStorage
from sowba.settings.model import ServiceStatus
from sowba.settings.model import StorageName
from sowba.registry import get as get_registry
from sowba.registry import add as add_registry
from sowba.settings.model import JwtAlgorithm
from sowba.security import roles
from sowba.settings.model import AppSettings
from sowba.cli.utils import load_raw_settings


from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException


app = typer.Typer()


class UserType(str, Enum):
    user: str = "user"
    admin: str = "admin"


def validate_email(email):
    try:
        email = EmailStr.validate(email)
    except EmailError as err:
        raise typer.BadParameter(str(err))
    return email


def add_auth_service(
    settings: AppSettings,
    secret_key: str = None,
    access_token_ttl: int = 30,
    storage: StorageName = StorageName.rocksdb,
    algorithm: JwtAlgorithm = JwtAlgorithm.hs256,
):
    raw_settings = load_raw_settings(settings.file)
    config_file = raw_settings.pop("file")
    auth = {
        "storage": {
            "model": f"{settings.name}.services.auth.model.User",
            "connector": storage,
        },
        "algorithm": JwtAlgorithm.hs256,
        "access_token_expire_minutes": access_token_ttl or 30,
    }
    if secret_key:
        auth["secret_key"] = secret_key
    raw_settings["auth"] = auth

    try:
        cookiecutter(
            f"{path.template.auth}",
            output_dir=f"{path.cwd()}/{settings.name}/services",
            no_input=True,
            extra_context={
                "auth": "auth",
                "storage": storage,
                "algorithm": JwtAlgorithm.hs256,
                "access_token_expire_minutes": access_token_ttl or 30,
            },
        )
        print(json.dumps(raw_settings, indent=4), file=open(config_file, "wt"))
    except OutputDirExistsException:
        typer.echo("Eroor: Auth alredy added!")
        raise typer.Abort()
    return AppSettings(file=config_file, **raw_settings)


def add_user(storage, username, emali, password, principals):
    breakpoint()
    storage.close()
    return
    ...


def load_auth_service(settings: AppSettings):
    ...


def load_auth_storage(storage: StorageName, settings: AppSettings):
    for sconf in settings.storages.connectors:
        if sconf.name == storage:
            stg = sconf.factory()
            stg.configure(
                settings.auth.storage.model,
                **getattr(sconf, "configuration", ConnectorConfig()).dict(),
            )
            stg.settings(**getattr(sconf, "settings", dict()))
            return stg
    else:
        return None
    # conf: ServiceStorage = settings.auth.storage
    # storage = make_auth_storage(srv.name, settings)
    # add_registry.storage("auth", storage)
    ...


@app.command()
def init(
    secret_key: str = typer.Option(None, "--secret-key"),
    algorithm: JwtAlgorithm = typer.Option(JwtAlgorithm.hs256, "--jwt-algo"),
    access_token_ttl: int = typer.Option(30, "--token-ttl"),
    root_emali: str = typer.Option(
        "root@sowba.com",
        prompt=True,
        confirmation_prompt=True,
        callback=validate_email,
    ),
    password: str = typer.Option(
        "ChangeMe", prompt=True, confirmation_prompt=True, hide_input=True
    ),
    storage: StorageName = typer.Option(StorageName.rocksdb),
):
    username = "root"
    principals = [f"{roles.root}"]

    settings = get_registry.app_settings()
    settings = add_auth_service(
        settings,
        storage=storage,
        algorithm=algorithm,
        secret_key=secret_key,
        access_token_ttl=access_token_ttl,
    )
    add_user(
        load_auth_storage(storage, settings),
        username,
        root_emali,
        password,
        principals,
    )


@app.command()
def add(user: UserType = typer.Argument(UserType.user)):
    # settings = get_registry.app_settings()
    breakpoint()
    return


if __name__ == "__main__":
    app()
