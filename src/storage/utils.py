from app.storage.memory import MemoryDB
from app.storage.rocksdb import RocksDBConnector


DB_CONNECTORS = {
    "RocksDBConnector": RocksDBConnector,
    "MemoryDB": MemoryDB
}


def init_db(name, *, connector=None, context=None, model=None):
    try:
        database = DB_CONNECTORS[connector](name, model=model)
        database.setup()
        context.set(database)
    except KeyError:
        raise Exception("Invalid Db Connector.")
    return context


def get_db(context):
    return context.get()
