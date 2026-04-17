import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.services.analyzer import AML_System


@pytest.fixture
def sample_transaction_data():
    # fake data to catch structuring
    data = [
        # Sender_A: 9500 total in 1 hour (hits flag)
        {"transaction_id": "T001", "sender_id": "Sender_A", "receiver_id": "Receiver_B", "amount": 4000, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 0)},
        {"transaction_id": "T002", "sender_id": "Sender_A", "receiver_id": "Receiver_B", "amount": 3000, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 15)},
        {"transaction_id": "T003", "sender_id": "Sender_A", "receiver_id": "Receiver_B", "amount": 2500, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 30)},
        # Sender_C: small amount (should be ignored)
        {"transaction_id": "T004", "sender_id": "Sender_C", "receiver_id": "Receiver_D", "amount": 500, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 0)},
    ]
    return pd.DataFrame(data)


def test_detect_structuring_attempts(sample_transaction_data):
    # checking if Sender_A is caught and Sender_C is skipped
    aml = AML_System(sample_transaction_data)
    time_window = timedelta(hours=1)
    results_df = aml.detect_structuring_attempts(time_window)

    # only 1 guy should be caught
    assert len(results_df) == 1
    result = results_df.iloc[0].to_dict()

    # check if it's the right sender and receiver
    assert result["sender_id"] == "Sender_A"
    assert result["receiver_id"] == "Receiver_B"
    # check if math matches (4000+3000+2500)
    assert result["summed_amount"] == 9500


@pytest.fixture
def additional_test_data():
    # more data for velocity and geo tests
    base_time = datetime(2024, 1, 1, 12, 0)
    data = []

    # Sender_V: 6 trans in few mins (breaks limit of 5)
    for i in range(6):
        data.append({
            "transaction_id": f"V{i}", "sender_id": "Sender_V", "receiver_id": "Rec_V",
            "amount": 100, "country": "US", "type": "transfer",
            "timestamp": base_time + timedelta(minutes=i)
        })

    # Sender_W: only 2 trans (he is clean)
    data.extend([
        {"transaction_id": "W1", "sender_id": "Sender_W", "receiver_id": "Rec_W", "amount": 100, "country": "US", "type": "transfer", "timestamp": base_time},
        {"transaction_id": "W2", "sender_id": "Sender_W", "receiver_id": "Rec_W", "amount": 100, "country": "US", "type": "transfer", "timestamp": base_time + timedelta(minutes=5)}
    ])

    # PA is for Panama, should hit geo inflow
    data.append({"transaction_id": "P1", "sender_id": "Sender_X", "receiver_id": "Rec_X", "amount": 5000, "country": "PA", "type": "transfer", "timestamp": base_time})
    data.append({"transaction_id": "P2", "sender_id": "Sender_Y", "receiver_id": "Rec_Y", "amount": 2000, "country": "PA", "type": "transfer", "timestamp": base_time})

    return pd.DataFrame(data)


def test_detect_high_velocity_transfers(additional_test_data):
    # checking if V hits velocity limit but W is ignored
    aml = AML_System(additional_test_data)
    results = aml.detect_high_velocity_transfers(timedelta(hours=1), frequency_limit=5)

    assert len(results) > 0
    flagged_senders = results["sender_id"].unique()
    assert "Sender_V" in flagged_senders
    assert "Sender_W" not in flagged_senders


def test_aggregate_geographic_inflow(additional_test_data):
    # checking if sum for Panama is exactly 7000
    aml = AML_System(additional_test_data)
    results = aml.aggregate_geographic_inflow()
    pa_data = results[results["country"] == "PA"]

    assert len(pa_data) == 1
    assert pa_data.iloc[0]["inflow"] == 7000


@pytest.fixture
def mixed_aml_data():
    # messy data to test unverified users and multi-sender structuring
    return pd.DataFrame([
        # first timer
        {"transaction_id": "N1", "sender_id": "Sender_New", "amount": 500, "country": "US", "timestamp": datetime(2024, 1, 1, 10, 0)},
        # returning user
        {"transaction_id": "O1", "sender_id": "Sender_Old", "amount": 500, "country": "US", "timestamp": datetime(2024, 1, 1, 10, 1)},
        {"transaction_id": "O2", "sender_id": "Sender_Old", "amount": 500, "country": "US", "timestamp": datetime(2024, 1, 1, 10, 2)},
        # multi-trans structuring
        {"transaction_id": "A1", "sender_id": "Sender_A", "amount": 4500, "country": "US", "timestamp": datetime(2024, 1, 1, 11, 0)},
        {"transaction_id": "A2", "sender_id": "Sender_A", "amount": 5000, "country": "US", "timestamp": datetime(2024, 1, 1, 11, 10)},
        # one big trans already in buffer
        {"transaction_id": "B1", "sender_id": "Sender_B", "amount": 9500, "country": "US", "timestamp": datetime(2024, 1, 1, 11, 20)}
    ])


def test_identify_unverified_originators(mixed_aml_data):
    # check if only users with 1 trans like Sender_New and B are flagged
    aml = AML_System(mixed_aml_data)
    results = aml.identify_unverified_originators()
    flagged_ids = results["sender_id"].unique()

    assert "Sender_New" in flagged_ids
    assert "Sender_B" in flagged_ids
    assert "Sender_Old" not in flagged_ids
    assert "Sender_A" not in flagged_ids
    # should be 2 guys total
    assert len(results) == 2


def test_structuring_multiple_senders_and_single_large_hit(mixed_aml_data):
    # checking if multi-trans and one big hit in buffer both get caught
    aml = AML_System(mixed_aml_data, target_limit=10000, buffer=1000)
    results = aml.detect_structuring_attempts(timedelta(hours=1))
    flagged_senders = results["sender_id"].unique()

    assert "Sender_A" in flagged_senders
    assert "Sender_B" in flagged_senders
    # 500 bucks shouldn't be here
    assert "Sender_New" not in flagged_senders


def test_structuring_isolation(mixed_aml_data):
    # making sure math for A doesn't mix with B
    aml = AML_System(mixed_aml_data)
    results = aml.detect_structuring_attempts(timedelta(hours=1))
    a2_result = results[results["transaction_id"] == "A2"].iloc[0]
    assert a2_result["summed_amount"] == 9500


def test_structuring_time_boundary():
    # check if 1 second difference resets the rolling window
    start_time = datetime(2024, 1, 1, 12, 0)
    data = [
        {"transaction_id": "T1", "sender_id": "A", "amount": 5000, "timestamp": start_time},
        {"transaction_id": "T2", "sender_id": "A", "amount": 4500, "timestamp": start_time + timedelta(minutes=59, seconds=59)},
        # T3 is outside the 1h window from T1
        {"transaction_id": "T3", "sender_id": "A", "amount": 1000, "timestamp": start_time + timedelta(hours=1, seconds=1)},
    ]
    aml = AML_System(pd.DataFrame(data))
    results = aml.detect_structuring_attempts(timedelta(hours=1))

    # T2 still has T1 in window (9500)
    assert "T2" in results["transaction_id"].values
    # T3 window dropped T1 (total 5500), so no flag
    assert "T3" not in results["transaction_id"].values


def test_init_parameter_validation():
    # checking if init fails with bullshit params
    df = pd.DataFrame([{"amount": 100}])
    # buffer too big
    with pytest.raises(ValueError, match="Buffer should be less than target limit"):
        AML_System(df, target_limit=5000, buffer=6000)
    # negative limits
    with pytest.raises(ValueError, match="Limits and buffer should be positive values"):
        AML_System(df, target_limit=-100, buffer=10)