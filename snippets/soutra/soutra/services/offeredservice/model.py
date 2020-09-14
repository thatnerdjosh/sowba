from sowba.core.model import SBaseModel


class Offeredservice(SBaseModel):
    uid: str
    name: str
    price: float
    is_available: bool
