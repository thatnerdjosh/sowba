from typing import List
from datetime import datetime
from contextvars import ContextVar
from pydantic import BaseModel, Field, SecretStr, EmailStr
from fastapi_permissions import Allow
from sowba.security import roles


class UserPrincipals(BaseModel):
    principals: List[str] = [roles.user]


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
    __acl__ = [(Allow, roles.admin, "view")]


class UserprincipalsAcl:
    __acl__ = [(Allow, roles.admin, "update")]

