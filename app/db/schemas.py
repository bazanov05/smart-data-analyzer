from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AmlReportCreate(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    country: str
    type: str


class AmlReportResponse(BaseModel):

    # Pydantic reads dicts by default, but SQLAlchemy objects use attributes not keys
    # from_attributes=True switches Pydantic to read via getattr() instead of dict access
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    country: str
    type: str
    id: int
    created_at: datetime
