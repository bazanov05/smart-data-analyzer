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
    summed_amount: float


class UnverifiedOriginatorCreate(CreateBase):
    num_of_transactions: int


class HighVelocityTransferCreate(CreateBase):
    time_gap: str
    frequency: int


class GeographicalInflowCreate(BaseModel):
    country: str
    inflow: float
    risk_level: str


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
    summed_amount: float


class UnverifiedOriginatorResponse(ResponseBase):
    num_of_transactions: int


class HighVelocityTransferResponse(ResponseBase):
    frequency: int


class GeographicalInflowResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    country: str
    inflow: float
    id: int
    risk_level: str
    created_at: datetime


class RawDataCreate(CreateBase):
    pass


class RawDataResponse(ResponseBase):
    pass
