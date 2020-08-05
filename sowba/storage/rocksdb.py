import gc
import uuid
import json
import rocksdb
from sowba.storage import DBConnector
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder



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
            return (True, json.dumps(existing_value).encode('utf-8'))
        return (True, value)

    def name(self):
        return b'UpdateData'


class RocksDBConnector(DBConnector):

    @property
    def uuid(self):
        return str(uuid.uuid1())

    def __init__(self, dbname, model=None):
        self.dbname = dbname
        self.model = model
        self.opts = rocksdb.Options()
        self.db = None

    def validate(self, obj):
        if not isinstance(obj, self.model):
            raise HTTPException(status_code=412)
        return True

    def serialize(self, obj):
        if self.validate(obj):
            return obj.json().encode("utf-8")

    def deserialize(self, obj):
        return self.model(**json.loads(obj))

    def setup(self):
        if self.db is None:
            self.opts.create_if_missing = True
            self.opts.max_open_files = 300000
            self.opts.write_buffer_size = 67108864
            self.opts.max_write_buffer_number = 3
            self.opts.target_file_size_base = 67108864
            self.opts.merge_operator = UpdateData()
            self.opts.table_factory = rocksdb.BlockBasedTableFactory(
                filter_policy=rocksdb.BloomFilterPolicy(10),
                block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
                block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2))
            )
        self.db = rocksdb.DB(f"{self.dbname}.db", self.opts)

    def close(self):
        if hasattr(self.db, '_db'):
            del self.db._db
            gc.collect()

    def store(self, oid=None, obj=None):
        oid = oid or self.uuid
        self.db.put(oid.encode("utf-8"), self.serialize(obj))
        return {
            "id": oid,
            "item": obj
        }

    def update(self, oid, obj):
        self.db.merge(
            oid.encode("utf-8"),
            json.dumps(
                jsonable_encoder(obj.dict(exclude_unset=True))
            ).encode("utf-8")
        )
        return {
            "id": oid,
            "item": obj.dict(exclude_unset=True)
        }

    def delete(self, oid):
        try:
            self.db.delete(oid.encode("utf-8"))
        except Exception:
            raise HTTPException(status_code=404)
        return {"deleted": True}

    def get_all(self):
        iter_item = self.db.iteritems()
        iter_item.seek_to_first()
        return [
            {
                "id": oid.decode(),
                "item": self.deserialize(obj)
            } for oid, obj in iter_item
        ]

    def get(self, oid: str):
        obj = self.db.get(oid.encode("utf-8"))
        if obj is None:
            raise HTTPException(status_code=404)
        return {"id": oid, "item": self.deserialize(obj)}

    def find(self, *args, **kwargs):
        ...
