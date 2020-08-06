from typing import List, Callable
import dataclasses as dcls
from collections import namedtuple
from fastapi_permissions import (
    Allow,
    Authenticated
)
from pydantic import BaseModel

class Acl(namedtuple('Acl', ('access', 'principal', 'permission'))):
    __slots__ = ()


class CreateItemAcl:
    __acl__ = [
        Acl(Allow, "role:user", "create"),
        Acl(Allow, "role:admin", "create"),
    ]

@dcls.dataclass
class AclPolicy:
    get: Callable = None
    create: CreateItemAcl = None


class BaseResourceAcl(BaseModel):

    def __acl__(self):
        assert self.owner is not None, "Owner must be define."
        return [
            Acl(Allow, "role:user", "create"),
            Acl(Allow, "role:admin", "create"),

            Acl(Allow, Authenticated, "view"),

            Acl(Allow, "role:admin", "update"),
            Acl(Allow, f"user:{self.owner}", "update"),

            Acl(Allow, "role:admin", "delete"),
            Acl(Allow, f"user:{self.owner}", "delete"),
        ]


default_acl_policy = AclPolicy(create=CreateItemAcl)
