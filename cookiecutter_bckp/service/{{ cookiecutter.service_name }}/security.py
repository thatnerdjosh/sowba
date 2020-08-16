import jwt
import asyncio
from typing import Union
from jwt import PyJWTError
from fastapi import Depends, HTTPException
from pydantic import ValidationError, EmailStr

from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from sowba.security import Everyone
from sowba.security import Authenticated
from sowba.security.model import User, UserInDB, USER_DB


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


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
