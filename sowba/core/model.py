import uuid
from typing import Set
from typing import List
from pydantic import Field
from datetime import datetime
from pydantic import EmailStr
from pydantic import BaseModel
from pydantic import create_model
from sowba.security.acl import SBaseModelAcl
from sowba.security.roles import SUserRoles


def get_in_db_model(model: BaseModel, name: str = None):
    name = name or f"{model.__name__}InDb"
    return create_model(name, owner=(str, ...), __base__=model)


class SBaseModel(SBaseModelAcl):
    uid: str = Field(default_factory=uuid.uuid1)
    owner: str = "anonymous"
    __searchable_fields__: Set[str] = set()


class SBaseUserModel(SBaseModel):
    username: str
    email: EmailStr
    first_name: str = None
    last_name: str = None
    hashed_password: str
    principals: List[SUserRoles] = [SUserRoles.user]
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updateed_on: datetime = Field(default_factory=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}"
