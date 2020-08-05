import json
import logging
import asyncio
import os
from copy import deepcopy
import hypercorn.asyncio
import hypercorn.config


logger = logging.getLogger(__name__)


default_settings = {
    "asgi": {
        # settings handed to asgi config
        "host": "0.0.0.0",
        "port": 8000,
        "timeout_keep_alive": 20,
        "proxy_headers": True,
        "log_level": "error",
        "http": "auto",
    },
    "__file__": None,
}


def hypercorn_factory(app, **settings):
    config = hypercorn.config.Config()
    config.bind = [f'{settings["host"]}:{settings["port"]}']
    config.debug = settings.get("debug") is True
    config.loglevel = settings.get("log_level") or "info"
    config.keep_alive_timeout = settings["timeout_keep_alive"]
    config.access_log_format = "[%(t)s] %(h)s %(S)s %(r)s %(s)s %(b)s %(D)s"
    return asyncio.run(hypercorn.asyncio.serve(app, config))


def load_configuration_file(configuration: str):
    if os.path.exists(configuration):
        with open(configuration, "r") as config:
            if configuration.lower().endswith(".json"):
                try:
                    settings = json.load(config)
                except json.decoder.JSONDecodeError:
                    logger.warning(
                        "Could not parse json configuration {}".format(
                            configuration
                        )
                    )
                    raise
        settings["__file__"] = configuration
        return settings
    else:
        raise Exception("Could not find settings")


def get_settings(configuration: str = None, overrides=None):
    settings = deepcopy(default_settings)
    if configuration is not None:
        settings.update(load_configuration_file(configuration))  # type: ignore
    if overrides is not None:
        settings.update(overrides)
    for env_name in os.environ.keys():
        if not env_name.startswith("O_"):
            continue
        name = env_name[2:].lower()
        value = os.environ[env_name]
        if value[0] in ("{", "["):
            value = json.loads(value)
        context = settings
        parts = name.split("__")
        for part in parts[:-1]:
            if part not in context:
                context[part] = {}  # type: ignore
            context = context[part]  # type: ignore
        context[parts[-1]] = value  # type: ignore

    return settings
