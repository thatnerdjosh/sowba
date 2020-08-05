import os
import uvicorn
import asyncio
import uvloop
import hypercorn.asyncio
import hypercorn.config
from sowba.core.settings import get_settings
from sowba.core.const import core_directory, resources_directory

from sowba.core.utils import resolve_dotted_name
from sowba.core.utils import run_app


def hypercorn_factory(app, **settings):
    config = hypercorn.config.Config()
    config.bind = [f'{settings["host"]}:{settings["port"]}']
    config.debug = settings.get("debug") is True
    config.loglevel = settings.get("log_level") or "info"
    config.keep_alive_timeout = settings["timeout_keep_alive"]
    config.access_log_format = "[%(t)s] %(h)s %(S)s %(r)s %(s)s %(b)s %(D)s"
    return asyncio.run(hypercorn.asyncio.serve(app, config))


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
    print(f"sowba service rm : {kwargs}")


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
    print(f"sowba service add : {kwargs}")


def service_action(action, **kwargs):
    {
        "ls": ls,
        "rm": rm,
        "run": run,
        "add": add,
    }[action](**kwargs)
