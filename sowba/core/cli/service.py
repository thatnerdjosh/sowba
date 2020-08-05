import os
import uvicorn
import asyncio
import uvloop
import hypercorn.asyncio
import hypercorn.config
from core.settings import get_settings
from core.app import run_app
from core.const import core_directory


def hypercorn_factory(app, **settings):
    config = hypercorn.config.Config()
    config.bind = [f'{settings["host"]}:{settings["port"]}']
    config.debug = settings.get("debug") is True
    config.loglevel = settings.get("log_level") or "info"
    config.keep_alive_timeout = settings["timeout_keep_alive"]
    config.access_log_format = "[%(t)s] %(h)s %(S)s %(r)s %(s)s %(b)s %(D)s"
    return asyncio.run(hypercorn.asyncio.serve(app, config))


def ls(**kwargs):
    coponents = filter(
        lambda c: c not in ['sowba.egg-info', 'core', 'template'],
        os.listdir(f"{core_directory}/..")
    )
    print(list(coponents))


def rm(**kwargs):
    print(f"sowba service rm : {kwargs}")


def start(**kwargs):
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

    print(f"sowba service start : {settings}")


def create(**kwargs):
    print(f"sowba service create : {kwargs}")


def service_action(action, **kwargs):
    {
        "ls": ls,
        "rm": rm,
        "start": start,
        "create": create,
    }[action](**kwargs)
