from sqlalchemy import Integer, Column, String, Numeric, DateTime
from app.db.database import Base
from sqlalchemy import func


class StructuringAttempt(Base):
    __tablename__ = "structuring_attempts"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)

    # index = True is to have rows grouped by, SQLite does it behind the scenes
    # and creates new structure

    sender_id = Column(String, nullable=False, index=True)
    receiver_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)  # 10 digits total, 2 after the point
    country = Column(String, nullable=False, index=True)  # db will reject Null countries
    type = Column(String, nullable=False)
    summed_amount = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())  # to get the time of report by getting the time of uploading on server


class UnverifiedOriginator(Base):
    __tablename__ = "unverified_originators"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)
    sender_id = Column(String, index=True, nullable=False)
    receiver_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    country = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    num_of_transactions = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class HighVelocityTransfer(Base):
    __tablename__ = "high_velocity_transfers"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)
    sender_id = Column(String, nullable=False, index=True)
    receiver_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    country = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    time_gap = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class GeographicalInflow(Base):
    __tablename__ = "geographical_inflows"

    id = Column(Integer, primary_key=True)
    country = Column(String, nullable=False, unique=True)
    inflow = Column(Numeric(10, 2), nullable=False)
    risk_level = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RawData(Base):
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)
    sender_id = Column(String, index=True, nullable=False)
    receiver_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    country = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class AISummary(Base):
    __tablename__ = "ai_summary"

    id = Column(Integer, primary_key=True)
    summary = Column(String, nullable=False)
    type = Column(String, nullable=False)
    report_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
