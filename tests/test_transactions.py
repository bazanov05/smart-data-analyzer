import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.transactions import app
from app.db.database import Base, get_db
from app.db.models import (
    StructuringAttempt,
    GeographicalInflow,
    UnverifiedOriginator,
    HighVelocityTransfer,
    RawData
)

# In-memory database setup WITH StaticPool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Now the tables will persist across connections
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def valid_csv_content():
    return (
        "transaction_id,sender_id,receiver_id,amount,country,type,timestamp\n"
        "TX001,Sender_A,Receiver_B,9500,US,transfer,2024-01-01 10:00:00\n"
        "TX002,Sender_A,Receiver_B,500,US,transfer,2024-01-01 10:15:00\n"
        "TX003,New_User,Receiver_C,100,UK,transfer,2024-01-01 11:00:00"
    )


@pytest.fixture
def invalid_csv_missing_cols():
    return (
        "transaction_id,sender_id,amount\n"
        "TX001,Sender_A,9500"
    )


def test_upload_csv_success(valid_csv_content):
    files = {"file": ("test.csv", valid_csv_content, "text/csv")}
    response = client.post("/update", files=files)

    assert response.status_code == 200
    data = response.json()

    # Check if all expected report types are in the response
    assert "Raw_data" in data
    assert "structuring_attempts" in data
    assert "unverified_originators" in data
    assert "geographical_inflows" in data
    assert "high_velocity_transfers" in data


def test_upload_csv_missing_columns(invalid_csv_missing_cols):
    files = {"file": ("test.csv", invalid_csv_missing_cols, "text/csv")}
    response = client.post("/update", files=files)

    assert response.status_code == 400
    # Checks if the API correctly returns a list of the missing columns
    assert isinstance(response.json()["detail"], list)


def test_upload_invalid_file_type():
    files = {"file": ("test.txt", "some text", "text/plain")}
    response = client.post("/update", files=files)

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported media type"


@pytest.fixture(autouse=True)
def setup_test_data():
    # Create fresh tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Insert a fake Structuring Attempt
    sa = StructuringAttempt(
        transaction_id="TX_SA_001", sender_id="S1", receiver_id="R1",
        amount=5000.0, country="US", type="transfer", summed_amount=9500.0,
        timestamp=datetime.now()
    )

    # Insert a fake Geographical Inflow
    geo = GeographicalInflow(
        country="PA", inflow=15000.0, risk_level="High-risk"
    )

    db.add(sa)
    db.add(geo)
    db.commit()
    db.close()

    yield # This is where the test runs

    # Destroy tables after the test so the next test gets a clean slate
    Base.metadata.drop_all(bind=engine)


def test_get_structuring_attempt_success():
    response = client.get("/reports/structuring_attempt/1")
    assert response.status_code == 200

    data = response.json()
    assert data["transaction_id"] == "TX_SA_001"
    assert data["country"] == "US"


def test_get_structuring_attempt_not_found():
    response = client.get("/reports/structuring_attempt/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Report with this id does not exist"


def test_get_geographical_inflow_success():
    response = client.get("/reports/geographical_inflow/1")
    assert response.status_code == 200

    data = response.json()
    assert data["country"] == "PA"
    assert data["risk_level"] == "High-risk"


def test_get_geographical_inflow_not_found():
    response = client.get("/reports/geographical_inflow/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Report with this id does not exist"