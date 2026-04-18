import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.repository import (
    create_structuring_attempt_report,
    get_structuring_attempt_report_by_id,
    get_all_structuring_attempts
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def valid_structuring_data():
    return {
        "transaction_id": "TX_STR_001",
        "sender_id": "Sender_A",
        "receiver_id": "Receiver_B",
        "amount": 3000.00,
        "country": "US",
        "type": "transfer",
        "summed_amount": 9500.00,
        "timestamp": datetime.now()
    }


def test_create_structuring_attempt_success(db_session, valid_structuring_data):
    report = create_structuring_attempt_report(db_session, valid_structuring_data)
    assert report is not None
    assert report.id is not None
    assert report.transaction_id == "TX_STR_001"
    assert float(report.summed_amount) == 9500.00


def test_create_structuring_attempt_duplicate_transaction_id(db_session, valid_structuring_data):
    # First creation succeeds
    create_structuring_attempt_report(db_session, valid_structuring_data)

    # Second creation with the same unique transaction_id must return None
    duplicate_report = create_structuring_attempt_report(db_session, valid_structuring_data)
    assert duplicate_report is None


def test_create_structuring_attempt_missing_required_field(db_session, valid_structuring_data):
    # Remove a nullable=False field
    del valid_structuring_data["amount"]

    # SQLAlchemy raises IntegrityError, your code catches it and returns None
    invalid_report = create_structuring_attempt_report(db_session, valid_structuring_data)
    assert invalid_report is None


def test_get_structuring_attempt_by_id_success(db_session, valid_structuring_data):
    created = create_structuring_attempt_report(db_session, valid_structuring_data)

    fetched = get_structuring_attempt_report_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.sender_id == "Sender_A"


def test_get_structuring_attempt_by_id_not_found(db_session):
    fetched = get_structuring_attempt_report_by_id(db_session, 999)
    assert fetched is None


def test_get_all_structuring_attempts_success(db_session, valid_structuring_data):
    create_structuring_attempt_report(db_session, valid_structuring_data)

    second_data = valid_structuring_data.copy()
    second_data["transaction_id"] = "TX_STR_002"
    create_structuring_attempt_report(db_session, second_data)

    all_reports = get_all_structuring_attempts(db_session)
    assert len(all_reports) == 2


def test_get_all_structuring_attempts_empty(db_session):
    all_reports = get_all_structuring_attempts(db_session)
    assert len(all_reports) == 0
    assert isinstance(all_reports, list)
