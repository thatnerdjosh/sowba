from sowba.security.acl import Acl


class CreateItemAcl:
    __acl__ = [
        Acl(Allow, "role:user", "create"),
        Acl(Allow, "role:admin", "create"),
    ]


@dcls.dataclass
class AclPolicy:
    get: Callable = None
    create: CreateItemAcl = None


default_acl_policy = AclPolicy(create=CreateItemAcl)
