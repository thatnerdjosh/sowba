import os

core_directory = os.path.dirname(os.path.realpath(__file__))
resources_directory = f"{core_directory}/../resources"
cookiecutter_directory = f"{core_directory}/../../cookiecutter"

BANNER: str = """
Ows interactive console.
- app
- settings
"""

DEFAULT_CORS = {"allow_origins": ["*"], "allow_headers": ["*"], "allow_methods": ["*"]}