import uuid
from app.storage import DBConnector
from fastapi.exceptions import HTTPException


class MemoryDB(DBConnector):

    DBS = dict()

    def setup(self):
        ...

    def close(self):
        ...

    def __init__(self, dbname, model=None):
        self.dbname = dbname
        self.model = model
        self.DBS.setdefault(dbname, dict())

    @property
    def uuid(self):
        return str(uuid.uuid1())

    def store(self, oid=None, obj=None):
        oid = oid or self.uuid
        self.DBS[self.dbname][oid] = obj
        return {
            "id": oid,
            "item": obj
        }

    def update(self, oid, obj):
        before_obj = self.DBS[self.dbname].get(oid)
        if before_obj is None:
            raise HTTPException(status_code=404)
        fields = list(
            filter(
                lambda d: d[1] != None,
                obj.dict(exclude_unset=True).items()
            )
        )
        for attr, value in fields:
            if isinstance(vars(before_obj)[attr], list):
                vars(before_obj)[attr] = list(
                    set(vars(before_obj)[attr] + value)
                )
            else:
                vars(before_obj)[attr] = value
        self.DBS[self.dbname][oid] = before_obj

        return {"id": oid, "item": before_obj}

    def delete(self, oid):
        try:
            del self.DBS[self.dbname][oid]
        except KeyError:
            raise HTTPException(status_code=404)

    def get_all(self):
        return [
            {
                "id": oid,
                "item": obj
            } for oid, obj in self.DBS[self.dbname].items()
        ]

    def get(self, oid: str):
        obj = self.DBS[self.dbname].get(oid)
        if obj is None:
            raise HTTPException(status_code=404)
        return {"id": oid, "item": obj}

    def find(self, *args, **kwargs):
        ...
