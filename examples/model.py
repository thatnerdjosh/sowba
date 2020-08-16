from pydantic import Field
from datetime import datetime
from sowba.core.model import SBaseModel


class User(SBaseModel):
    name: str
    age: int
    created_on: datetime = Field(default_factory=datetime.now)
