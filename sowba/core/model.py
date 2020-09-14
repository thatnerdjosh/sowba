import uuid
from typing import Set
from pydantic import Field
from pydantic import BaseModel
from pydantic import create_model
from sowba.security.acl import SBaseModelAcl


def create_in_db_model(model: BaseModel, name: str = None):
    name = name or f"{model.__name__}InDb"
    return create_model(name, owner=(str, ...), __base__=model)


class SBaseModel(SBaseModelAcl):
    uid: str = Field(default_factory=uuid.uuid1)
    __searchable_fields__: Set[str] = set()


class SBaseModelInDb(BaseModel):
    owner: str = "anonymous@sowba.com"
