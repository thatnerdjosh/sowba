from typing import List
from app.core import api
from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel, Field
from contextvars import ContextVar
from app.resources.lodges.model import (
    Event,
    Contact,
    Location,
    MembershipFee
)



router = APIRouter()
db_context = ContextVar("lodge_db_context")


@api(router, db_connector="RocksDBConnector", context=db_context)
class Lodge(BaseModel):
    name: str = None
    avatar: str = None
    info_status: str = None
    bio: str = None
    mantra: str = None
    contact: Contact = None
    location: Location = None
    officers: List[str] = None
    founding_date: datetime = None
    main_room: str = None
    information_room: str = None
    rooms: List[str] = None
    trestle_board: List[Event] = None
    membership_fee: MembershipFee = None


# @router.on_event("startup")
# def init_db():
#     print(db_context.get())
