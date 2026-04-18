import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.repository import (
    create_structuring_attempt_report,
    get_structuring_attempt_report_by_id,
    get_all_structuring_attempts,
    create_unverified_originator_report,
    get_unverified_originator_report_by_id,
    get_all_unverified_originators,
    create_high_velocity_transfer_report,
    get_high_velocity_transfer_report_by_id,
    get_all_high_velocity_transfers,
    create_geographical_inflow_report,
    get_geographical_inflow_report_by_id,
    get_all_geographical_inflows,
    create_raw_data_report,
    get_raw_data_report,
    get_all_raw_data,
    create_ai_summary_report,
    get_ai_summary_report,
    get_all_ai_summaries
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


@pytest.fixture
def valid_unverified_data():
    return {
        "transaction_id": "TX_UV_001",
        "sender_id": "New_User_1",
        "receiver_id": "Receiver_X",
        "amount": 500.00,
        "country": "UK",
        "type": "transfer",
        "num_of_transactions": 1,
        "timestamp": datetime.now()
    }


def test_create_unverified_originator_success(db_session, valid_unverified_data):
    report = create_unverified_originator_report(db_session, valid_unverified_data)
    assert report is not None
    assert report.id is not None
    assert report.transaction_id == "TX_UV_001"
    assert report.num_of_transactions == 1


def test_create_unverified_originator_duplicate_transaction(db_session, valid_unverified_data):
    # First insert works
    create_unverified_originator_report(db_session, valid_unverified_data)

    # Second insert with same transaction_id should be caught by IntegrityError and return None
    duplicate = create_unverified_originator_report(db_session, valid_unverified_data)
    assert duplicate is None


def test_create_unverified_originator_missing_field(db_session, valid_unverified_data):
    # Remove mandatory 'country' field
    del valid_unverified_data["country"]

    invalid_report = create_unverified_originator_report(db_session, valid_unverified_data)
    assert invalid_report is None


def test_get_unverified_originator_by_id_success(db_session, valid_unverified_data):
    created = create_unverified_originator_report(db_session, valid_unverified_data)

    fetched = get_unverified_originator_report_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.sender_id == "New_User_1"


def test_get_unverified_originator_by_id_not_found(db_session):
    fetched = get_unverified_originator_report_by_id(db_session, 999)
    assert fetched is None


def test_get_all_unverified_originators_success(db_session, valid_unverified_data):
    create_unverified_originator_report(db_session, valid_unverified_data)

    second_data = valid_unverified_data.copy()
    second_data["transaction_id"] = "TX_UV_002"
    second_data["sender_id"] = "New_User_2"
    create_unverified_originator_report(db_session, second_data)

    all_reports = get_all_unverified_originators(db_session)
    assert len(all_reports) == 2


def test_get_all_unverified_originators_empty(db_session):
    all_reports = get_all_unverified_originators(db_session)
    assert len(all_reports) == 0
    assert isinstance(all_reports, list)


@pytest.fixture
def valid_high_velocity_data():
    return {
        "transaction_id": "TX_HV_001",
        "sender_id": "Fast_Sender_A",
        "receiver_id": "Receiver_Y",
        "amount": 100.00,
        "country": "US",
        "type": "transfer",
        "frequency": 8,
        "timestamp": datetime.now(),
        "time_gap": "00:05:00"  # model expects a String here
    }


def test_create_high_velocity_transfer_success(db_session, valid_high_velocity_data):
    report = create_high_velocity_transfer_report(db_session, valid_high_velocity_data)
    assert report is not None
    assert report.id is not None
    assert report.transaction_id == "TX_HV_001"
    assert report.frequency == 8
    assert report.time_gap == "00:05:00"


def test_create_high_velocity_transfer_duplicate(db_session, valid_high_velocity_data):
    # First insert works
    create_high_velocity_transfer_report(db_session, valid_high_velocity_data)

    # Second insert with the same transaction_id should fail safely
    duplicate = create_high_velocity_transfer_report(db_session, valid_high_velocity_data)
    assert duplicate is None


def test_create_high_velocity_transfer_missing_field(db_session, valid_high_velocity_data):
    # Remove mandatory 'frequency' field
    del valid_high_velocity_data["frequency"]

    invalid_report = create_high_velocity_transfer_report(db_session, valid_high_velocity_data)
    assert invalid_report is None


def test_get_high_velocity_by_id_success(db_session, valid_high_velocity_data):
    created = create_high_velocity_transfer_report(db_session, valid_high_velocity_data)

    fetched = get_high_velocity_transfer_report_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.sender_id == "Fast_Sender_A"


def test_get_high_velocity_by_id_not_found(db_session):
    fetched = get_high_velocity_transfer_report_by_id(db_session, 999)
    assert fetched is None


def test_get_all_high_velocity_transfers_success(db_session, valid_high_velocity_data):
    create_high_velocity_transfer_report(db_session, valid_high_velocity_data)

    second_data = valid_high_velocity_data.copy()
    second_data["transaction_id"] = "TX_HV_002"
    second_data["frequency"] = 12
    create_high_velocity_transfer_report(db_session, second_data)

    all_reports = get_all_high_velocity_transfers(db_session)
    assert len(all_reports) == 2


def test_get_all_high_velocity_transfers_empty(db_session):
    all_reports = get_all_high_velocity_transfers(db_session)
    assert len(all_reports) == 0
    assert isinstance(all_reports, list)


@pytest.fixture
def valid_geo_data():
    return {
        "country": "PA",
        "inflow": 7500.50,
        "risk_level": "High-risk"
    }


def test_create_geographical_inflow_success(db_session, valid_geo_data):
    report = create_geographical_inflow_report(db_session, valid_geo_data)
    assert report is not None
    assert report.id is not None
    assert report.country == "PA"
    assert float(report.inflow) == 7500.50


def test_create_geographical_inflow_duplicate_country(db_session, valid_geo_data):
    # First insert for Panama succeeds
    create_geographical_inflow_report(db_session, valid_geo_data)

    # Second insert for Panama MUST fail because country is unique=True
    duplicate = create_geographical_inflow_report(db_session, valid_geo_data)
    assert duplicate is None


def test_create_geographical_inflow_missing_field(db_session, valid_geo_data):
    # Remove mandatory 'risk_level' field
    del valid_geo_data["risk_level"]

    invalid_report = create_geographical_inflow_report(db_session, valid_geo_data)
    assert invalid_report is None


def test_get_geographical_inflow_by_id_success(db_session, valid_geo_data):
    created = create_geographical_inflow_report(db_session, valid_geo_data)

    fetched = get_geographical_inflow_report_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.country == "PA"


def test_get_geographical_inflow_by_id_not_found(db_session):
    fetched = get_geographical_inflow_report_by_id(db_session, 999)
    assert fetched is None


def test_get_all_geographical_inflows_success(db_session, valid_geo_data):
    create_geographical_inflow_report(db_session, valid_geo_data)

    # Add a second, different country
    second_data = {
        "country": "US",
        "inflow": 1200.00,
        "risk_level": "Low-risk"
    }
    create_geographical_inflow_report(db_session, second_data)

    all_reports = get_all_geographical_inflows(db_session)
    assert len(all_reports) == 2


def test_get_all_geographical_inflows_empty(db_session):
    all_reports = get_all_geographical_inflows(db_session)
    assert len(all_reports) == 0
    assert isinstance(all_reports, list)


@pytest.fixture
def valid_raw_data():
    return {
        "transaction_id": "TX_RAW_001",
        "sender_id": "Sender_R",
        "receiver_id": "Receiver_R",
        "amount": 100.50,
        "country": "CA",
        "type": "transfer",
        "timestamp": datetime.now()
    }


def test_create_raw_data_success(db_session, valid_raw_data):
    report = create_raw_data_report(db_session, valid_raw_data)
    assert report is not None
    assert report.id is not None
    assert report.transaction_id == "TX_RAW_001"
    assert report.country == "CA"


def test_create_raw_data_duplicate_transaction(db_session, valid_raw_data):
    # First insert
    create_raw_data_report(db_session, valid_raw_data)

    # Second insert with same unique transaction_id should fail safely
    duplicate = create_raw_data_report(db_session, valid_raw_data)
    assert duplicate is None


def test_create_raw_data_missing_field(db_session, valid_raw_data):
    # Remove mandatory 'amount' field
    del valid_raw_data["amount"]

    invalid_report = create_raw_data_report(db_session, valid_raw_data)
    assert invalid_report is None


def test_get_raw_data_by_id_success(db_session, valid_raw_data):
    created = create_raw_data_report(db_session, valid_raw_data)

    fetched = get_raw_data_report(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.sender_id == "Sender_R"


def test_get_raw_data_by_id_not_found(db_session):
    fetched = get_raw_data_report(db_session, 999)
    assert fetched is None


def test_get_all_raw_data_success(db_session, valid_raw_data):
    create_raw_data_report(db_session, valid_raw_data)

    second_data = valid_raw_data.copy()
    second_data["transaction_id"] = "TX_RAW_002"
    second_data["sender_id"] = "Sender_Z"
    create_raw_data_report(db_session, second_data)

    all_reports = get_all_raw_data(db_session)
    assert len(all_reports) == 2


def test_get_all_raw_data_empty(db_session):
    all_reports = get_all_raw_data(db_session)
    assert len(all_reports) == 0
    assert isinstance(all_reports, list)


@pytest.fixture
def valid_ai_summary():
    # Note: 'report_id' is nullable=True in schema, so it's optional but good to test
    return {
        "summary": "This user is exhibiting smurfing behavior.",
        "type": "structuring_analysis",
        "report_id": 1
    }


def test_create_ai_summary_success(db_session, valid_ai_summary):
    report = create_ai_summary_report(db_session, valid_ai_summary)
    assert report is not None
    assert report.id is not None
    assert report.type == "structuring_analysis"
    assert report.report_id == 1


def test_create_ai_summary_missing_field(db_session, valid_ai_summary):
    # 'summary' is nullable=False
    del valid_ai_summary["summary"]

    invalid_report = create_ai_summary_report(db_session, valid_ai_summary)
    assert invalid_report is None


def test_create_ai_summary_without_report_id(db_session, valid_ai_summary):
    # report_id is allowed to be null, so this should succeed
    del valid_ai_summary["report_id"]

    report = create_ai_summary_report(db_session, valid_ai_summary)
    assert report is not None
    assert report.report_id is None


def test_get_ai_summary_by_id_success(db_session, valid_ai_summary):
    created = create_ai_summary_report(db_session, valid_ai_summary)

    fetched = get_ai_summary_report(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert "smurfing behavior" in fetched.summary


def test_get_ai_summary_by_id_not_found(db_session):
    fetched = get_ai_summary_report(db_session, 999)
    assert fetched is None


def test_get_all_ai_summaries_success(db_session, valid_ai_summary):
    create_ai_summary_report(db_session, valid_ai_summary)

    second_summary = {
        "summary": "High risk geographic transfer detected.",
        "type": "geo_analysis"
    }
    create_ai_summary_report(db_session, second_summary)

    all_reports = get_all_ai_summaries(db_session)
    assert len(all_reports) == 2


def test_get_all_ai_summaries_empty(db_session):
    all_reports = get_all_ai_summaries(db_session)
    assert len(all_reports) == 0
    assert isinstance(all_reports, list)
