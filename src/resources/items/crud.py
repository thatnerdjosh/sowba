from src.core import api
from fastapi import APIRouter
from contextvars import ContextVar
from src.resources.items.model import (
    BaseItem, ItemType
)

router = APIRouter()
db_context = ContextVar("item_db_context")


@api(router, db_connector="RocksDBConnector", context=db_context)
class Item(BaseItem):
    name: str = None
    type: ItemType = None
