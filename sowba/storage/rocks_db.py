import gc
import json
import rocksdb
import operator
import functools
from typing import List
from pydantic import BaseModel
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from sowba.core import path
from sowba.storage import BaseStorage
from sowba.core.model import SBaseModel


def validator(obj: BaseModel, model: BaseModel = None) -> bool:
    if isinstance(obj, model):
        return True
    return False


def serialize(obj: BaseModel, model: BaseModel = None) -> bytes:
    if not validator(obj, model=model):
        raise Exception(f"{obj} is not serializable.")
    return obj.json().encode("utf-8")


def deserialize(obj: bytes, model: BaseModel = None) -> BaseModel:
    return model(**json.loads(obj))


def default_filter(field, value, obj, opr="eq"):
    """
    Containment Test	obj in seq	contains(seq, obj)
    Truth Test	obj	truth(obj)
    Ordering	a < b	lt(a, b)
    Ordering	a <= b	le(a, b)
    Equality	a == b	eq(a, b)
    Difference	a != b	ne(a, b)
    Ordering	a >= b	ge(a, b)
    Ordering	a > b	gt(a, b)
    """
    OPERATORS = {
        "exists",
        "in",
        "lt",
        "le",
        "eq",
        "ne",
        "ge",
        "gt",
    }
    assert opr in OPERATORS, "find operation: invalid operator"
    if opr == "in":
        field = vars(obj).get(field)
        if not isinstance(field, (str, list, tuple, set, frozenset)):
            field = list()
        return operator.contains(field, value)
    if opr == "exists":
        return operator.truth(vars(obj).get(field))
    return vars(operator)[opr](vars(obj).get(field), value)


class UpdateData(rocksdb.interfaces.AssociativeMergeOperator):
    def merge(self, key, existing_value, value):
        if existing_value:
            existing_value = json.loads(existing_value)
            value = json.loads(value)
            for attr, val in value.items():
                if isinstance(value[attr], list):
                    existing_value[attr] = list(
                        set(existing_value[attr] + val)
                    )
                else:
                    existing_value[attr] = val
            return (True, json.dumps(existing_value).encode("utf-8"))
        return (True, value)

    def name(self):
        return b"UpdateData"


TABLE_FACTORY = rocksdb.BlockBasedTableFactory(
    filter_policy=rocksdb.BloomFilterPolicy(10),
    block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
    block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)),
)


class RocksDBStorage(BaseStorage):
    default_settings = {
        "create_if_missing": True,
        "max_open_files": 300000,
        "write_buffer_size": 67108864,
        "max_write_buffer_number": 3,
        "target_file_size_base": 67108864,
        "merge_operator": UpdateData(),
        "table_factory": TABLE_FACTORY,
    }

    def __init__(self):
        self.db = None
        self.model = None
        self._db_collected = False
        self.opts = rocksdb.Options(**self.default_settings)

    @property
    def dbpath(self):
        return f"{path.cwd()}/rocksdbs"

    def count(self):
        value = 0
        if self.db is None:
            return value
        iterdb = self.db.iterkeys()
        iterdb.seek_to_first()
        for i in iterdb:
            value += 1
        return value

    def settings(self, **kwargs):
        super().settings(**kwargs)
        for opt, value in self.getsettings().items():
            try:
                getattr(self.opts, opt)
            except AttributeError:
                raise Exception(f"RocksDb invalid options: {opt}")
            setattr(self.opts, opt, value)
        self._setuped = True

    def configure(self, model: BaseModel, /, **kwargs):
        kwargs.setdefault("deserialize", deserialize)
        kwargs.setdefault("serialize", serialize)
        kwargs.setdefault("validator", validator)
        super().configure(model, **kwargs)
        self._configured = True

    def setup(self):
        assert self.model, "RocksDb storage must be configured!"
        try:
            getattr(self, "_configured")
        except AttributeError:
            Exception("RocksDb storage must be configured!")

        if not getattr(self, "_setuped", None):
            self.settings()

        if self.db:
            self.close()

        path.pathlib.Path(self.dbpath).mkdir(exist_ok=True)
        self.db = rocksdb.DB(f"{self.dbpath}/{self.dbname}.db", self.opts)

    def close(self):
        """
        https://github.com/twmht/python-rocksdb/issues/10
        """
        del self.db
        gc.collect()

    def store(self, obj=None):
        oid = str(obj.uid)
        self.db.put(oid.encode("utf-8"), self.serialize(obj, model=self.model))
        return {"id": oid, "item": obj}

    def get(self, oid: str):
        obj = self.db.get(oid.encode("utf-8"))
        if obj is None:
            raise HTTPException(status_code=404)
        return {"id": oid, "item": self.deserialize(obj, model=self.model)}

    def getmany(self, *oids: List[str]) -> List[BaseModel]:
        return [
            {
                "id": oid.decode(),
                "item": self.deserialize(obj, model=self.model),
            }
            for oid, obj in self.db.multi_get(
                [oid.encode("utf8") for oid in oids]
            ).items()
        ]

    def getall(self):
        iterdb = self.db.iteritems()
        iterdb.seek_to_first()
        return [
            {
                "id": oid.decode(),
                "item": self.deserialize(obj, model=self.model),
            }
            for oid, obj in iterdb
        ]

    def find(
        self, field, value, opr="eq", key=default_filter,
    ):
        iterdb = self.db.itervalues()
        iterdb.seek_to_first()
        deserializer = functools.partial(self.deserialize, model=self.model)
        return map(
            lambda obj: {"id": obj.uid, "item": obj},
            filter(
                functools.partial(key, field, value, opr=opr),
                map(deserializer, iterdb),
            ),
        )

    def delete(self, oid: str):
        try:
            self.db.delete(oid.encode("utf-8"))
        except Exception:
            raise HTTPException(status_code=404)
        return {"id": oid, "deleted": True}

    def update(self, oid, obj):
        self.db.merge(
            oid.encode("utf-8"),
            json.dumps(jsonable_encoder(obj.dict(exclude_unset=True))).encode(
                "utf-8"
            ),
        )
        return {"id": oid, "item": obj.dict(exclude_unset=True)}


if __name__ == "__main__":
    from pydantic import Field
    from datetime import datetime

    class User(SBaseModel):
        name: str
        age: int
        created_on: datetime = Field(default_factory=datetime.now)

    def create_user(count=7):
        for i in range(count):
            for name in {"sekou", "oumar", "idrissa", "cheick"}:
                storage.store(obj=User(name=name, age=i + 30))

    storage = RocksDBStorage()
    storage.configure(User, dbname="rocksdb_users")
    storage.settings()
    storage.setup()
    # do something
    create_user()
    # print(storage.getall())
    # print(
    #     storage.getmany(
    #         "534ff084-db75-11ea-b934-acde48001122",
    #         "7c94a2d2-db75-11ea-9b29-acde48001122",
    #     )
    # )
    print(storage.count())
    print(storage.getall())
    print(list(storage.find("name", "e", opr="in")))
    storage.close()
