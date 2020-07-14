from pydantic import BaseModel
from datetime import datetime


class MembershipFee(BaseModel):
    amount: float
    start_date: datetime
    end_date: datetime


class Event(BaseModel):
    event_id: str
    date: datetime
    description: str
    subject: str


class Location(BaseModel):
    lng: float
    lat: float


class Contact(BaseModel):
    email: str
    phone: str
    address: str
