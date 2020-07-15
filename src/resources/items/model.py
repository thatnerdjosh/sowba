from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from src.security.acl import BaseResource


class ItemType(str, Enum):
    foo = "foo"
    bar = "bar"


class BaseItem(BaseResource):
    created_on: datetime = Field(default_factory=datetime.utcnow)
