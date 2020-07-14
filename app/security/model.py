from typing import List
from datetime import datetime
from contextvars import ContextVar
from app.storage.utils import init_db, get_db
from pydantic import BaseModel, Field, SecretStr ,EmailStr, validator
from .acl import default_resource_acl
from fastapi_permissions import Allow


class BaseObj(BaseModel):
    _owner: str = None

    @property
    def owner(self):
        return self._owner

    __acl__ = default_resource_acl


class UserPrincipals(BaseModel):
    principals: List[str] = []


class Updateprincipals(BaseModel):
    add: List[str] = []
    delete: List[str] = []

class UserData(BaseModel):
    first_name: str
    last_name: str


class User(UserData, UserPrincipals):
    username: str
    email: EmailStr

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserSignup(User):
    password: SecretStr
    confirm_password: SecretStr


class UserInDB(User):
    hashed_password: str
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updateed_on: datetime = Field(default_factory=datetime.utcnow)


class UpdatePasswd(BaseModel):
    current_password: SecretStr
    password: SecretStr
    confirm_password: SecretStr

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class UserListAcl:
    __acl__ = [(Allow, 'role:admin', "view")]


class UserprincipalsAcl:
    __acl__ = [(Allow, 'role:admin', "update")]



db_context = init_db(
    "users_storage",
    connector="RocksDBConnector",
    context=ContextVar("user_db_context"),
    model=UserInDB
)
USER_DB = get_db(db_context)
