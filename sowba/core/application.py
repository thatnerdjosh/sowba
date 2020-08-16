import asyncio
from functools import wraps
from fastapi import FastAPI
from fastapi import APIRouter

from starlette.middleware.cors import CORSMiddleware

from sowba.settings.app import AppSettings
from sowba.storage.utils import get_storage
from sowba.storage.utils import get_service_conf

from sowba.core.crud import SServiceCrud


class SServiceRouter(APIRouter):
    def __init__(
        self, *args, servicename: str, app_settings: AppSettings, **kwargs
    ):
        super().__init__(*args, **kwargs)
        assert app_settings
        self.tag = f"{app_settings.name}@{servicename}"
        self.prefix = f"/{app_settings.name}/{servicename}"
        self.conf = get_service_conf(servicename, app_settings)
        self.storage = get_storage(
            servicename, app_settings, connector=self.conf.settings.storage
        )
        self.on_startup.append(self.start_storage)
        self.on_shutdown.append(self.stop_storage)

    async def start_storage(self):
        if asyncio.iscoroutinefunction(self.storage):
            await self.storage.setup()
        else:
            self.storage.setup()
        print("Started Storage")

    async def stop_storage(self):
        if asyncio.iscoroutinefunction(self.storage):
            await self.storage.close()
        else:
            self.storage.close()
        print("Closed Storage")


class SService:
    def __init__(self, router: SServiceRouter, name=None):
        self.router = router

    def __call__(self, cls):
        crud = SServiceCrud(cls)

        crud.get = self.router.get("/{oid}")(crud.get)
        crud.get_many = self.router.get("/")(crud.get_many)
        crud.create = self.router.post("/@create")(crud.create)
        crud.create_many = self.router.post("/@create/")(crud.create_many)
        crud.patch = self.router.patch("/@update/{oid}")(crud.patch)
        crud.patch_many = self.router.patch("/@update/")(crud.patch_many)
        crud.put = self.router.put("/@upsert/{oid}")(crud.put)
        crud.put_many = self.router.put("/@upsert/")(crud.put_many)
        crud.delete = self.router.delete("/@delete/{oid}")(crud.delete)
        crud.delete_many = self.router.delete("/@delete/")(crud.delete_many)

        @wraps(cls)
        def inner(*args, **kwargs):
            return cls(*args, **kwargs)

        return inner


class SApp(FastAPI):

    settings = None

    def __init__(self, *args, settings: AppSettings = None, **kwargs):
        self.settings = settings
        super().__init__(*args, **kwargs)

    def configure(self, settings: AppSettings):
        self.settings = settings
        self.add_middleware(CORSMiddleware, **self.settings.cors.dict())

    def setup_task_vars(self):
        ...
