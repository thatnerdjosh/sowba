from pydantic import FilePath
from pydantic.parse import load_file
from sowba.settings.app import AppSettings


def load_settings(configfile: FilePath) -> AppSettings:
    return AppSettings(file=configfile, **load_file(configfile))
