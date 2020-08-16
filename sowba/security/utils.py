import jwt
import asyncio
from datetime import datetime, timedelta
from fastapi import HTTPException
from pydantic import EmailStr
from passlib.context import CryptContext


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "1fe11dfa433ce37f4abe64c28cd70d2a27f9a6244df7394de0b2826fafd03d86"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_access_token(*, data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def principals_validator(principals):
    for principal in principals:
        if len(principal.split(":")) != 2:
            raise HTTPException(
                status_code=412, detail=f"Invalid pricipal format: {principal}"
            )
    return principals
