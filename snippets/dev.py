import re
import pydantic
from datetime import datetime
from pydantic import BaseModel, Field, PyObject


class User(BaseModel):
    name: str
    age: int
    klass: PyObject
    created_on: datetime = Field(default_factory=datetime.now)


if __name__ == "__main__":
    u = User(name="Sekou", age=35, klass="examples.model.User")
    # for k, v in vars(u).items():
    #     if isinstance(v, pydantic.main.ModelMetaclass):
    #         vars(u)[k] = re.search("'(.+?)'", str(u.klass)).group(1)
    print(u.json(indent=4))
