from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CreateBase(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    country: str
    type: str
    timestamp: datetime


class StructuringAttemptCreate(CreateBase):
    pass


class UnverifiedOriginatorCreate(CreateBase):
    sender_id: str | None = None


class HighVelocityTransferCreate(CreateBase):
    timegap: str


class GeographicalInflowCreate(BaseModel):
    country: str
    inflow: float


class ResponseBase(BaseModel):

    # SQLite does not return dicts, but objects
    # so we need to take values from attributes, not dicts
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    country: str
    type: str
    timestamp: datetime
    id: int
    created_at: datetime


class StructuringAttemptResponse(ResponseBase):
    pass


class UnverifiedOriginatorResponse(ResponseBase):
    sender_id: str | None = None


class HighVelocityTransferResponse(ResponseBase):
    timegap: str


class GeographicalInflowResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    country: str
    inflow: float
    id: int
    created_at: datetime
