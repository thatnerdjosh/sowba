from typing import List


class SServiceCrud:
    def __init__(self, model, /):
        self.model = model

        async def get(oid: str):
            return {"endpoint": f"[GET] /{oid}"}

        self.get = get

        async def get_many():
            return {"endpoint": "[GET] /"}

        self.get_many = get_many

        async def create(obj: self.model):
            return {"endpoint": "[POST] /@create"}

        self.create = create

        async def create_many(obj: self.model):
            return {"endpoint": "[POST] /@create/"}

        self.create_many = create_many

        async def put(oid: str, obj: self.model):
            return {"endpoint": "[PUT] /@put/{oid}"}

        self.put = put

        async def put_many(objs: List[self.model]):
            return {"endpoint": "[PUT] /@put/"}

        self.put_many = put_many

        async def patch(oid: str, obj: self.model):
            return {"endpoint": f"[PATCH] /@patch/{oid}"}

        self.patch = patch

        async def patch_many(objs: List[self.model]):
            return {"endpoint": "[PATCH] /@patch/"}

        self.patch_many = patch_many

        self.put_many = put_many

        async def delete(oid: str):
            return {"endpoint": f"[DELETE] /@delete/{oid}"}

        self.delete = delete

        async def delete_many(objs: List[self.model]):
            return {"endpoint": "[DELETE] /@delete/"}

        self.delete_many = delete_many
