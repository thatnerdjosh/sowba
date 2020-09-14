import pathlib
from typing import Dict
from pydantic import FilePath
from pydantic.parse import load_file
from sowba.settings.model import AppSettings


def load_raw(config: FilePath = pathlib.Path("./config.json")) -> Dict:
    return {"file": config, **load_file(config)}


def load(config: FilePath = pathlib.Path("./config.json")) -> AppSettings:
    return AppSettings(**load_raw(config))
