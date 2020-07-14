from typing import List
import dataclasses as dcls
from collections import namedtuple
from fastapi_permissions import (
    Allow,
    Authenticated
)


class Acl(namedtuple('Acl', ('access', 'principal', 'permission'))):
    __slots__ = ()


@dcls.dataclass
class AclPolicy:
    create: List[Acl] = dcls.field(default_factory=list)
    update: List[Acl] = dcls.field(default_factory=list)
    delete: List[Acl] = dcls.field(default_factory=list)
    view: List[Acl] = dcls.field(default_factory=list)

    @property
    def all(self):
        return [
            dcls.asdict(self)[field.name]
            for field in dcls.fields(self)
        ]


default_acl_policy = AclPolicy(
    view=[Acl(Allow, Authenticated, "view")],
    create=[Acl(Allow, "role:admin", "create")],
    update=[Acl(Allow, "role:admin", "update")],
    delete=[Acl(Allow, "role:admin", "delete")]
)


def default_resource_acl(self):
    assert self.owner is not None, "Owner must be define."
    return [
        *default_acl_policy.all,
        Acl(Allow, f"user:{self.owner}", "update"),
        Acl(Allow, f"user:{self.owner}", "delete"),
    ]
