import asyncio
from fastapi import Depends
from functools import wraps
from pydantic import create_model
from src.storage.memory import MemoryDB
from src.storage.rocksdb import RocksDBConnector

from src.security.acl import default_acl_policy
from src.security.model import User
from src.security.routes import Permission
from src.security.utils import get_current_user


def create_in_db_model(model):
    return create_model(
        f"{model.__name__}InDb",
        owner=(str, ...),
        __base__=model
    )


class api:

    DB_CONNECTORS = {
        "RocksDBConnector": RocksDBConnector,
        "MemoryDB": MemoryDB
    }

    def __init__(
        self,
        router,
        *,
        db_connector="MemoryDB",
        context=None,
        acl_policy=default_acl_policy
    ):
        self.router = router
        self.db_connector = db_connector
        self.database = None
        self.context = context
        self.acl_policy = acl_policy

    def __call__(self, cls):

        clsInDb = create_in_db_model(cls)
        self.database = self.DB_CONNECTORS[self.db_connector](
            cls.__name__, model=clsInDb
        )
        self.database.setup()
        self.context.set(self.database)

        async def get_resource(oid):
            if asyncio.iscoroutinefunction(self.database.get):
                res = await self.database.get(oid)
            else:
                res = self.database.get(oid)
            return res["item"]

        if self.acl_policy.get is None:
            self.acl_policy.get = get_resource

        @self.router.get("/@crud/", tags=[f"{cls.__name__} CRUD"])
        async def get_items(
            current_user: User = Depends(get_current_user)
        ):
            if asyncio.iscoroutinefunction(self.database.get_all):
                return await self.database.get_all()
            return self.database.get_all()

        @self.router.get("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def get_item(
            oid: str,
            current_user: User = Depends(get_current_user),
            item: clsInDb = Permission("view", self.acl_policy.get)
        ):
            return {"id": oid, "item": item}

        @self.router.post("/@crud/", tags=[f"{cls.__name__} CRUD"])
        async def create_item(
            obj: cls,
            current_user: User = Depends(get_current_user),
            acl: list = Permission("create", self.acl_policy.create)
        ):
            obj = clsInDb(**{**obj.dict(), "owner": current_user.email})
            if asyncio.iscoroutinefunction(self.database.store):
                return await self.database.store(obj=obj)
            return self.database.store(obj=obj)

        @self.router.put("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def put_item(
            oid: str,
            obj: cls,
            current_user: User = Depends(get_current_user),
            acl: list = Permission("create", self.acl_policy.create)
        ):
            obj = clsInDb(**{**obj.dict(), "owner": current_user.email})
            if asyncio.iscoroutinefunction(self.database.store):
                return await self.database.store(oid=oid, obj=obj)
            return self.database.store(oid=oid, obj=obj)

        @self.router.patch("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def update_item(
            oid: str,
            obj: cls,
            current_user: User = Depends(get_current_user),
            item: clsInDb = Permission("update", self.acl_policy.get),
        ):
            obj = clsInDb(**{**item.dict(), **obj.dict(exclude_unset=True)})
            if asyncio.iscoroutinefunction(self.database.update):
                return await self.database.update(oid, obj)
            return self.database.update(oid, obj)

        @self.router.delete("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def delete_item(
            oid: str,
            current_user: User = Depends(get_current_user),
            item: clsInDb = Permission("delete", self.acl_policy.get),
        ):
            if asyncio.iscoroutinefunction(self.database.delete):
                return await self.database.delete(oid)
            return self.database.delete(oid)

        @wraps(cls)
        def inner(*args, **kwargs):
            return cls(*args, **kwargs)

        return inner
