import asyncio
from fastapi import Depends
from functools import wraps
from pydantic import create_model
from app.storage.memory import MemoryDB
from app.storage.rocksdb import RocksDBConnector

from app.security.model import User
from app.security.utils import get_current_user

class api:

    DB_CONNECTORS = {
        "RocksDBConnector": RocksDBConnector,
        "MemoryDB": MemoryDB
    }

    def __init__(self, router, *, db_connector="MemoryDB", context=None):
        self.router = router
        self.db_connector = db_connector
        self.database = None
        self.context = context

    def __call__(self, cls):
        clsInDb = create_model(f"{cls.__name__}InDb", owner=(str, ...))
        self.database = self.DB_CONNECTORS[self.db_connector](
            cls.__name__, model=clsInDb
        )
        self.database.setup()
        self.context.set(self.database)

        @self.router.get("/@crud/", tags=[f"{cls.__name__} CRUD"])
        async def get_items(current_user: User = Depends(get_current_user)):
            if asyncio.iscoroutinefunction(self.database.get_all):
                return await self.database.get_all()
            return self.database.get_all()

        @self.router.get("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def get_item(oid: str):
            if asyncio.iscoroutinefunction(self.database.get):
                return await self.database.get(oid)
            return self.database.get(oid)

        @self.router.post("/@crud/", tags=[f"{cls.__name__} CRUD"])
        async def create_item(obj: cls, current_user: User = Depends(get_current_user)):
            obj = clsInDb({**obj.dict(), "owner": current_user.email})
            if asyncio.iscoroutinefunction(self.database.store):
                return await self.database.store(obj=obj)
            return self.database.store(obj=obj)

        @self.router.put("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def put_item(oid: str, obj: cls, current_user: User = Depends(get_current_user)):
            obj = clsInDb({**obj.dict(), "owner": current_user.email})
            if asyncio.iscoroutinefunction(self.database.store):
                return await self.database.store(oid=oid, obj=obj)
            return self.database.store(oid=oid, obj=obj)

        @self.router.patch("/@crud/" + "{oid}", tags=[f"{cls.__name__} CRUD"])
        async def update_item(oid: str, obj: cls, current_user: User = Depends(get_current_user)):
            obj = clsInDb({**obj.dict(), "owner": current_user.email})
            if asyncio.iscoroutinefunction(self.database.update):
                return await self.database.update(oid, obj)
            return self.database.update(oid, obj)

        @wraps(cls)
        def inner(*args, **kwargs):
            return cls(*args, **kwargs)

        return inner
