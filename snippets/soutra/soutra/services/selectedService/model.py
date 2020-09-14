from sowba.security import Deny
from sowba.security import roles
from sowba.security.acl import Acl
from sowba.core.model import SBaseModel


class Selectedservice(SBaseModel):
    uid: str
    quantity: int
    discount: float = 0.0
    offered_service_uid: str

    __searchable_fields__ = {"quantity", "discount"}

    def __acl__(self):
        return [
            Acl(Deny, roles.admin, "create")
        ]