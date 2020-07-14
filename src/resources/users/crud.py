from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.core import api
from fastapi import APIRouter
from contextvars import ContextVar


router = APIRouter()
db_context = ContextVar("lodge_db_context")


@api(router, db_connector="RocksDBConnector", context=db_context)
class User(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    principals: List[str] = []
    created_on: datetime = None
    updateed_on: datetime = None
