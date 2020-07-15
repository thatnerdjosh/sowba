import logging
import argparse
from core.cli.consumer import consumer_action
from core.cli.service import service_action
from core.cli.producer import produser_action

logger = logging.getLogger(__name__)


def component_action(component: str, action, **kwargs):
    return {
        "service": service_action,
        "consumer": consumer_action,
        "produser": produser_action,
    }[component](action, **kwargs)


def cli_runner():

    parser = argparse.ArgumentParser()
    parser.add_argument("component", choices=["service", "consumer", "produser"])
    subparsers = parser.add_subparsers(dest="action")

    subparsers.add_parser("ls")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("component_name")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("component_name")
    start_parser.add_argument("--config", default="config.json")
    start_parser.add_argument("--host", type=str, default="0.0.0.0")
    start_parser.add_argument("--port", type=int, default=5000)
    start_parser.add_argument("--repica", type=int, default=None)
    start_parser.add_argument("--uvloop", action="store_true", default=False)
    start_parser.add_argument("--server", default="uvicorn")
    start_parser.add_argument("--reload", action="store_true", default=False)

    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("component_name")

    rm_parser = subparsers.add_parser("rm")
    rm_parser.add_argument("component_name")

    arguments, _ = parser.parse_known_args()
    component = vars(arguments).pop("component")
    action = vars(arguments).pop("action")
    component_action(component, action, **vars(arguments))

    # if arguments.uvloop:
    #     asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # settings = get_settings(arguments.configuration)
    # if arguments.port:
    #     settings["asgi"]["port"] = arguments.port
    # if arguments.host:
    #     settings["asgi"]["host"] = arguments.host
    # if arguments.reload:
    #     settings["asgi"]["reload"] = True

    # if arguments.server == "uvicorn":
    #     server_factory = uvicorn.run
    # elif arguments.server == "hypercorn":
    #     server_factory = hypercorn_factory

    # run_app(arguments.module, settings, factory=server_factory)


if __name__ == "__main__":
    cli_runner()
