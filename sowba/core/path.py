import os
import pathlib


def cwd() -> pathlib.Path:
    return pathlib.Path(os.path.realpath(os.path.curdir))


def core() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def root() -> pathlib.Path:
    return core().parent


def cookiecutter() -> pathlib.Path:
    return pathlib.Path(f"{root().parent}/cookiecutter")


class Template:
    @property
    def app(self) -> pathlib.Path:
        return pathlib.Path(f"{cookiecutter()}/app")

    @property
    def service(self) -> pathlib.Path:
        return pathlib.Path(f"{cookiecutter()}/service")


template = Template()
