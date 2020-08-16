from enum import Enum


class SUserRoles(str, Enum):
    user: str = "role:user"
    admin: str = "role:admin"
    root: str = "role:root"
