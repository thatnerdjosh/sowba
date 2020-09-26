from typing import List
from pydantic import BaseModel, parse_obj_as
from sowba.core import SServiceRouter
from sowba.settings.model import AppSettings, Route
from sowba.storage import BaseStorage


class SServiceCrud:
    class Meta:
        def __init__(self):
            self._routes = [
                {
                    "router_method": "post",
                    "method": "create",
                    "endpoint": "/"
                }
            ]

    def __init__(self, model: BaseModel, storage: BaseStorage):
        self.model = model
        self.storage = storage

        async def get(oid: str):
            return {"endpoint": f"[GET] /{oid}"}

        async def get_many():
            return {"endpoint": "[GET] /"}

        async def create(obj: self.model):
            return {"endpoint": "[POST] /@create"}

        async def create_many(obj: self.model):
            return {"endpoint": "[POST] /@create/"}

        async def put(oid: str, obj: self.model):
            return {"endpoint": "[PUT] /@put/{oid}"}

        async def put_many(objs: List[self.model]):
            return {"endpoint": "[PUT] /@put/"}

        async def patch(oid: str, obj: self.model):
            return {"endpoint": f"[PATCH] /@patch/{oid}"}

        async def patch_many(objs: List[self.model]):
            return {"endpoint": "[PATCH] /@patch/"}

        async def delete(oid: str):
            return {"endpoint": f"[DELETE] /@delete/{oid}"}

        async def delete_many(objs: List[self.model]):
            return {"endpoint": "[DELETE] /@delete/"}

        self.get = get
        self.put = put
        self.patch = patch
        self.create = create
        self.delete = delete
        self.get_many = get_many
        self.put_many = put_many
        self.patch_many = patch_many
        self.delete_many = delete_many


class api:
    def __init__(
        self, router: SServiceRouter, storage: BaseStorage, settings: AppSettings, name=None
    ):
        self.router = router
        self.storage = storage
        self.name = name
        self.settings = settings

    def __call__(self, cls):
        # TODO: Add configuration object to import custom ServiceCrud object
        crud = SServiceCrud(cls, storage=self.storage)
        autoload = parse_obj_as(List[Route], crud.Meta()._routes)
        for route in autoload:
            router_method = getattr(self.router, str.lower(route.router_method))
            crud_method = getattr(crud, route.method)
            setattr(crud, route.method, router_method(route.endpoint)(crud_method))

            # crud.get_many = self.router.get("/")(crud.get_many)
            # crud.create = self.router.post("/")(crud.create)
            # crud.patch = self.router.patch("/{oid}")(crud.patch)
            # crud.patch_many = self.router.patch("/")(crud.patch_many)
            # crud.put = self.router.put("/{oid}")(crud.put)
            # crud.put_many = self.router.put("/")(crud.put_many)
            # crud.delete = self.router.delete("/{oid}")(crud.delete)
            # crud.delete_many = self.router.delete("/")(crud.delete_many)

        def inner(*args, **kwargs):
            return cls(*args, **kwargs)

        return inner
