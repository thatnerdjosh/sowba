import asyncio
from fastapi import APIRouter
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sowba.security.model import (
    Token,
    User,
    UserSignup,
    UserInDB,
    UpdatePasswd,
    UserData,
    UserListAcl,
    Updateprincipals,
    UserprincipalsAcl,
    USER_DB
)

from sowba.security.utils import (
    create_access_token,
    authenticate_user,
    get_active_principals,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    principals_validator,
    pwd_context
)

from fastapi_permissions import configure_permissions



router = APIRouter()
Permission = configure_permissions(get_active_principals)


@router.get("/users/", tags=["Security"])
async def users(
    acl: UserListAcl = Permission("view", UserListAcl),
    current_user: User = Depends(get_current_user)
):
    if asyncio.iscoroutinefunction(USER_DB.get_all):
        return await USER_DB.get_all()
    return USER_DB.get_all()


@router.post("/users/@update_principals/{uid}", tags=["Security"])
async def update_principals(
    uid: str,
    principals: Updateprincipals,
    acl: UserprincipalsAcl = Permission("update", UserprincipalsAcl),
    current_user: User = Depends(get_current_user)
):
    if asyncio.iscoroutinefunction(USER_DB.get):
        user = await USER_DB.get(uid)
    else:
        user = USER_DB.get(uid)

    user = user["item"]
    for action in principals.fields:
        principals_validator(vars(principals)[action])
        if action == "add":
            user.principals = list(
                set(user.principals + principals.add))
        elif action == "delete":
            user.principals = list(
                set(user.principals) - set(principals.delete))

    if asyncio.iscoroutinefunction(USER_DB.store):
        response = await USER_DB.store(oid=user.email, obj=user)
    else:
        response = USER_DB.store(oid=user.email, obj=user)

    response["item"] = User(**user.dict())
    return response


@router.post("/token", response_model=Token, tags=["Security"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(
        USER_DB, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/@me", response_model=User, tags=["Security"])
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users/@update_passwd", tags=["Security"])
async def update_passwd(
    password: UpdatePasswd,
    current_user: User = Depends(get_current_user)
):
    return password


@router.post("/users/@update_user", tags=["Security"])
async def update_user(
    data: UserData,
    current_user: User = Depends(get_current_user)
):
    return data


@router.post("/users/@signup", tags=["Security"])
async def signup(new_user: UserSignup):
    if new_user.password != new_user.confirm_password:
        raise HTTPException(
                status_code=412,
                detail="Invalid confirmation password!"
            )
    new_user = UserInDB(
        **{
            **new_user.dict(),
            "hashed_password": pwd_context.hash(
                new_user.password.get_secret_value()
            )
        }
    )
    new_user.principals = [
        *{*new_user.principals, f"user:{new_user.email}", "role:user"}
    ]
    response = USER_DB.store(oid=new_user.email, obj=new_user)
    response["item"] = User(**new_user.dict())
    return response
