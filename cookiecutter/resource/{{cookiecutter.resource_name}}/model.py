from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from sowba.security.acl import BaseResourceAcl


class {{ cookiecutter.resource_name|capitalize }}Type(str, Enum):
    foo = "foo"
    bar = "bar"


class Base{{ cookiecutter.resource_name|capitalize }}(BaseResourceAcl):
    created_on: datetime = Field(default_factory=datetime.utcnow)
