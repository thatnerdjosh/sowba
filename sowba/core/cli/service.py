import os
import re
import shutil
import uvicorn
import asyncio
import uvloop
import hypercorn.asyncio
import hypercorn.config
from sowba.core.settings import get_settings
from sowba.core.const import core_directory, resources_directory, cookiecutter_directory

from sowba.core.utils import resolve_dotted_name
from sowba.core.utils import run_app

from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException


def hypercorn_factory(app, **settings):
    config = hypercorn.config.Config()
    config.bind = [f'{settings["host"]}:{settings["port"]}']
    config.debug = settings.get("debug") is True
    config.loglevel = settings.get("log_level") or "info"
    config.keep_alive_timeout = settings["timeout_keep_alive"]
    config.access_log_format = "[%(t)s] %(h)s %(S)s %(r)s %(s)s %(b)s %(D)s"
    return asyncio.run(hypercorn.asyncio.serve(app, config))


def clean_name(name):
    return re.sub('\W|^(?=\d)','_', name)


def ls(**kwargs):
    services = filter(
        lambda c: c not in ['__init__.py', '__pycache__'],
        os.listdir(resources_directory)
    )
    for service_name in services:
        print(f"{service_name}:")
        service = resolve_dotted_name(f"sowba.resources.{service_name}")
        for route in service.router.routes:
            print(f"{route.methods} => {service_name}{route.path}\t{route.name}")
        print("\n")


def rm(**kwargs):
    component_name = clean_name(kwargs["component_name"])
    try:
        shutil.rmtree(f'{resources_directory}/{component_name}')
    except OSError as e:
        print("Error: %s - %s." % (component_name, e.strerror))



def run(**kwargs):
    settings = get_settings(kwargs["config"])
    if kwargs["uvloop"]:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    if kwargs["port"]:
        settings["asgi"]["port"] = kwargs["port"]

    if kwargs["host"]:
        settings["asgi"]["host"] = kwargs["host"]

    if kwargs["reload"]:
        settings["asgi"]["reload"] = True

    if kwargs["server"] == "uvicorn":
        server_factory = uvicorn.run
    elif kwargs["server"] == "hypercorn":
        server_factory = hypercorn_factory

    run_app(settings, factory=server_factory)


def add(**kwargs):
    component_name = clean_name(kwargs["component_name"])
    try:
        r = cookiecutter(
            f"{cookiecutter_directory}/resource",
            output_dir=resources_directory,
            no_input=True,
            extra_context={
                'resource_name': component_name,
                'storage': kwargs["storage"]
            }
        )
        print(r)
    except OutputDirExistsException:
        print(f"Error: Service {component_name} already exists")


def service_action(action, **kwargs):
    {
        "ls": ls,
        "rm": rm,
        "run": run,
        "add": add,
    }[action](**kwargs)
