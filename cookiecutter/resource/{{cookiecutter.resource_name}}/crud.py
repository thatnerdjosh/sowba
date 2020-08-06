from sowba.core import api
from fastapi import APIRouter
from contextvars import ContextVar
from sowba.resources.{{ cookiecutter.resource_name }}.model import (
    Base{{ cookiecutter.resource_name|capitalize }}, {{ cookiecutter.resource_name|capitalize }}Type
)

router = APIRouter()
db_context = ContextVar("{{ cookiecutter.resource_name }}_db_context")


@api(router, db_connector="RocksDBConnector", context=db_context)
class {{ cookiecutter.resource_name|capitalize }}(Base{{ cookiecutter.resource_name|capitalize }}):
    name: str = None
    type: {{ cookiecutter.resource_name|capitalize }}Type = None
