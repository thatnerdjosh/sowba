import logging
import argparse
import uvloop
import asyncio
import uvicorn
from sowba.core.cli.consumer import consumer_action
from sowba.core.cli.service import service_action
from sowba.core.cli.producer import produser_action


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
    add_parser = subparsers.add_parser("add")
    rm_parser = subparsers.add_parser("rm")
    run_parser = subparsers.add_parser("run")
    arguments, _ = parser.parse_known_args()

    if arguments.component == "service":
        add_parser.add_argument("component_name")
        add_parser.add_argument(
            "--storage",
            default="memory",
            choices=["rocksdb", "memory"],
        )

        rm_parser.add_argument("component_name")

        run_parser.add_argument("--config", default="config.json")
        run_parser.add_argument("--host", type=str)
        run_parser.add_argument("--port", type=int)
        run_parser.add_argument("--server", default="uvicorn")
        run_parser.add_argument("--reload", action="store_true", default=False)
        run_parser.add_argument("--uvloop", action="store_true", default=True)

    if arguments.component in ("consumer", "produser"):
        run_parser.add_argument("component_name")
        run_parser.add_argument("--repica", type=int, default=None)
 

    arguments, _ = parser.parse_known_args()
    component = vars(arguments).pop("component")
    action = vars(arguments).pop("action")
    component_action(component, action, **vars(arguments))


if __name__ == "__main__":
    cli_runner()
