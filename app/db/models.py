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
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())  # to get the time of report by getting the time of uploading on server


class UnverifiedOriginator(Base):
    __tablename__ = "unverified_originators"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)
    sender_id = Column(String, index=True)   # nullable intentionally - unverified means sender_id is missing
    receiver_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    country = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
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
    timestamp = Column(DateTime, nullable=False)
    timegap = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class GeographicalInflow(Base):
    __tablename__ = "geographical_inflows"
    id = Column(Integer, primary_key=True)
    country = Column(String, nullable=False)
    inflow = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
