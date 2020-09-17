from typing import Callable
import dataclasses as dcls
from pydantic import BaseModel
from collections import namedtuple

from sowba.security import Allow
from sowba.security import Authenticated
from sowba.security import roles


class Acl(namedtuple("Acl", ("access", "principal", "permission"))):
    __slots__ = ()


class CreateItemAcl:
    __acl__ = [
        Acl(Allow, roles.user, "create"),
        Acl(Allow, roles.admin, "create"),
        Acl(Allow, roles.root, "create"),
    ]


@dcls.dataclass
class AclPolicy:
    get: Callable = None
    create: CreateItemAcl = None


class SBaseModelAcl(BaseModel):
    def __acl__(self):
        try:
            getattr(self, "owner")
        except AttributeError:
            Exception("Owner must be define.")

        return [
            Acl(Allow, roles.user, "create"),
            Acl(Allow, roles.admin, "create"),
            Acl(Allow, Authenticated, "view"),
            Acl(Allow, roles.admin, "update"),
            Acl(Allow, f"user:{self.owner}", "update"),
            Acl(Allow, roles.admin, "delete"),
            Acl(Allow, f"user:{self.owner}", "delete"),
        ]


default_acl_policy = AclPolicy(create=CreateItemAcl)
