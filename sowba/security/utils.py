import jwt
import asyncio
from typing import Union
from jwt import PyJWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from pydantic import ValidationError, EmailStr

from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from fastapi_permissions import (
    Everyone,
    Authenticated
)

from passlib.context import CryptContext
from sowba.security.model import User, UserInDB, USER_DB


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "1fe11dfa433ce37f4abe64c28cd70d2a27f9a6244df7394de0b2826fafd03d86"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def email_is_available(email):
    ...


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(db, email: EmailStr):
    try:
        if asyncio.iscoroutinefunction(db.get):
            user = await db.get(email)
        else:
            user = db.get(email)
    except HTTPException:
        return
    return user["item"]


async def authenticate_user(
    user_db, email: EmailStr, password: str
) -> Union[bool, UserInDB]:
    user = await get_user(user_db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (PyJWTError, ValidationError):
        raise credentials_exception
    user = await get_user(USER_DB, email)
    if user is None:
        raise credentials_exception
    return user


def get_active_principals(user: User = Depends(get_current_user)):
    if user:
        # user is logged in
        principals = [Everyone, Authenticated]
        principals.extend(getattr(user, "principals", []))
    else:
        # user is not logged in
        principals = [Everyone]
    return principals


def principals_validator(principals):
    for principal in principals:
        if len(principal.split(":")) != 2:
            raise HTTPException(
                    status_code=412,
                    detail=f"Invalid pricipal format: {principal}")
    return principals
