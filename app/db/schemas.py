from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RawDataCreate(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    country: str
    type: str
    timestamp: datetime


class StructuringAttemptCreate(RawDataCreate):
    summed_amount: float


class UnverifiedOriginatorCreate(RawDataCreate):
    num_of_transactions: int


class HighVelocityTransferCreate(RawDataCreate):
    time_gap: str
    frequency: int


class GeographicalInflowCreate(BaseModel):
    country: str
    inflow: float
    risk_level: str


class RawDataResponse(BaseModel):

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


class StructuringAttemptResponse(RawDataResponse):
    summed_amount: float


class UnverifiedOriginatorResponse(RawDataResponse):
    num_of_transactions: int


class HighVelocityTransferResponse(RawDataResponse):
    frequency: int


class GeographicalInflowResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    country: str
    inflow: float
    id: int
    risk_level: str
    created_at: datetime


class AISummaryCreate(BaseModel):
    summary: str    # was missing — agent generates this
    type: str
    report_id: int | None = None  # None for general summaries not tied to a specific report


class AISummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    summary: str
    type: str
    report_id: int | None = None  # matches the model
    created_at: datetime
