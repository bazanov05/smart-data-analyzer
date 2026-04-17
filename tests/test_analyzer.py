import pytest
import pandas as pd
from datetime import datetime, timedelta
from app.services.analyzer import AML_System


@pytest.fixture
def sample_transaction_data():
    """Creates a fake DataFrame specifically designed to trigger a structuring alert."""
    data = [
        # Structuring Attempt: Sender_A sends $9,500 total to Receiver_B within 1 hour
        {"transaction_id": "T001", "sender_id": "Sender_A", "receiver_id": "Receiver_B", "amount": 4000, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 0)},
        {"transaction_id": "T002", "sender_id": "Sender_A", "receiver_id": "Receiver_B", "amount": 3000, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 15)},
        {"transaction_id": "T003", "sender_id": "Sender_A", "receiver_id": "Receiver_B", "amount": 2500, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 30)},

        # Normal Transaction: Should NOT be flagged
        {"transaction_id": "T004", "sender_id": "Sender_C", "receiver_id": "Receiver_D", "amount": 500, "country": "US", "type": "transfer", "timestamp": datetime(2024, 1, 1, 10, 0)},
    ]
    return pd.DataFrame(data)


def test_detect_structuring_attempts(sample_transaction_data):
    """
    Given a dataset with 3 transactions totaling $9,500 under 1 hour,
    the AML_System should flag Sender_A and ignore Sender_C.
    """
    # Initialize your system with the fake data
    aml = AML_System(sample_transaction_data)

    # Run the method you built
    time_window = timedelta(hours=1)
    results_df = aml.detect_structuring_attempts(time_window)

    # Check 1: Did it find exactly 1 structuring group?
    assert len(results_df) == 1, "Should only find one structuring attempt."

    # Check 2: Extract the first row of the results as a dictionary
    result = results_df.iloc[0].to_dict()

    # Check 3: Did it flag the right person?
    assert result["sender_id"] == "Sender_A"
    assert result["receiver_id"] == "Receiver_B"

    # Check 4: Did it sum the math correctly? (4000 + 3000 + 2500 = 9500)
    # Adjust 'summed_amount' to whatever you actually named the column in your Pandas logic!
    assert result["summed_amount"] == 9500


@pytest.fixture
def additional_test_data():
    base_time = datetime(2024, 1, 1, 12, 0)
    data = []

    # High Velocity: Sender_V makes 6 quick transactions (limit is 5)
    for i in range(6):
        data.append({
            "transaction_id": f"V{i}", "sender_id": "Sender_V", "receiver_id": "Rec_V",
            "amount": 100, "country": "US", "type": "transfer",
            "timestamp": base_time + timedelta(minutes=i)
        })

    # Normal Velocity: Sender_W makes only 2 transactions
    data.extend([
        {"transaction_id": "W1", "sender_id": "Sender_W", "receiver_id": "Rec_W", "amount": 100, "country": "US", "type": "transfer", "timestamp": base_time},
        {"transaction_id": "W2", "sender_id": "Sender_W", "receiver_id": "Rec_W", "amount": 100, "country": "US", "type": "transfer", "timestamp": base_time + timedelta(minutes=5)}
    ])

    # Geo Inflow: Transfers from a specific country (e.g., PA for Panama)
    data.append({"transaction_id": "P1", "sender_id": "Sender_X", "receiver_id": "Rec_X", "amount": 5000, "country": "PA", "type": "transfer", "timestamp": base_time})
    data.append({"transaction_id": "P2", "sender_id": "Sender_Y", "receiver_id": "Rec_Y", "amount": 2000, "country": "PA", "type": "transfer", "timestamp": base_time})

    return pd.DataFrame(data)


def test_detect_high_velocity_transfers(additional_test_data):
    aml = AML_System(additional_test_data)

    # Looking for more than 5 transactions within 1 hour
    results = aml.detect_high_velocity_transfers(timedelta(hours=1), frequency_limit=5)

    assert len(results) > 0, "Should have flagged at least one sender."

    flagged_senders = results["sender_id"].unique()
    assert "Sender_V" in flagged_senders, "Sender_V should be flagged."
    assert "Sender_W" not in flagged_senders, "Sender_W should NOT be flagged."


def test_aggregate_geographic_inflow(additional_test_data):
    aml = AML_System(additional_test_data)
    results = aml.aggregate_geographic_inflow()

    # Looking for aggregated data for PA
    pa_data = results[results["country"] == "PA"]

    assert len(pa_data) == 1, "Should have exactly one row for PA."
    assert pa_data.iloc[0]["inflow"] == 7000, "Total amount for PA should be 7000."


@pytest.fixture
def mixed_aml_data():
    """Dataset for unverified originators and multi-sender structuring."""
    return pd.DataFrame([
        # Sender_New: Only 1 transaction (Unverified)
        {"transaction_id": "N1", "sender_id": "Sender_New", "amount": 500, "country": "US", "timestamp": datetime(2024, 1, 1, 10, 0)},

        # Sender_Old: 2 transactions (Verified)
        {"transaction_id": "O1", "sender_id": "Sender_Old", "amount": 500, "country": "US", "timestamp": datetime(2024, 1, 1, 10, 1)},
        {"transaction_id": "O2", "sender_id": "Sender_Old", "amount": 500, "country": "US", "timestamp": datetime(2024, 1, 1, 10, 2)},

        # Sender_A: Multi-transaction structuring ($9,500 total)
        {"transaction_id": "A1", "sender_id": "Sender_A", "amount": 4500, "country": "US", "timestamp": datetime(2024, 1, 1, 11, 0)},
        {"transaction_id": "A2", "sender_id": "Sender_A", "amount": 5000, "country": "US", "timestamp": datetime(2024, 1, 1, 11, 10)},

        # Sender_B: Single large transaction in buffer ($9,500)
        {"transaction_id": "B1", "sender_id": "Sender_B", "amount": 9500, "country": "US", "timestamp": datetime(2024, 1, 1, 11, 20)}
    ])


def test_identify_unverified_originators(mixed_aml_data):
    """Checks if users with exactly one transaction are flagged."""
    aml = AML_System(mixed_aml_data)
    results = aml.identify_unverified_originators()

    flagged_ids = results["sender_id"].unique()

    # Both Sender_New and Sender_B have only 1 transaction in this dataset
    assert "Sender_New" in flagged_ids
    assert "Sender_B" in flagged_ids
    assert "Sender_Old" not in flagged_ids
    assert "Sender_A" not in flagged_ids

    # The length should be 2 because two different senders match the criteria
    assert len(results) == 2


def test_structuring_multiple_senders_and_single_large_hit(mixed_aml_data):
    """
    Verifies that structuring flags both:
    1. Multiple transactions totaling near $10k.
    2. Single transactions already within the buffer.
    """
    aml = AML_System(mixed_aml_data, target_limit=10000, buffer=1000)
    results = aml.detect_structuring_attempts(timedelta(hours=1))

    flagged_senders = results["sender_id"].unique()

    # Sender_A should be flagged on the 2nd transaction (A2)
    assert "Sender_A" in flagged_senders

    # Sender_B should be flagged even with only one transaction (B1)
    # because 9500 is in the [9000, 10000) range.
    assert "Sender_B" in flagged_senders

    # Check that Sender_New (500) was ignored
    assert "Sender_New" not in flagged_senders


def test_structuring_isolation(mixed_aml_data):
    """Ensures amounts from different senders do not bleed into each other's totals."""
    aml = AML_System(mixed_aml_data)
    results = aml.detect_structuring_attempts(timedelta(hours=1))

    # Sender_A's rolling total at A2 should be exactly 9500
    a2_result = results[results["transaction_id"] == "A2"].iloc[0]
    assert a2_result["summed_amount"] == 9500


def test_structuring_time_boundary():
    """Ensures transactions exactly 1 second outside the window are excluded."""
    start_time = datetime(2024, 1, 1, 12, 0)
    data = [
        {"transaction_id": "T1", "sender_id": "A", "amount": 5000, "timestamp": start_time},
        {"transaction_id": "T2", "sender_id": "A", "amount": 4500, "timestamp": start_time + timedelta(minutes=59, seconds=59)},
        # Change amount to 1000. T2 + T3 will now be 5500, which is NOT suspicious.
        {"transaction_id": "T3", "sender_id": "A", "amount": 1000, "timestamp": start_time + timedelta(hours=1, seconds=1)},
    ]
    aml = AML_System(pd.DataFrame(data))
    results = aml.detect_structuring_attempts(timedelta(hours=1))

    # T2 should be flagged (Total 9500 includes T1)
    assert "T2" in results["transaction_id"].values

    # T3 should NOT be flagged (Total 5500 because T1 was dropped)
    assert "T3" not in results["transaction_id"].values


def test_init_parameter_validation():
    """Verifies that the system raises ValueError for invalid business logic params."""
    df = pd.DataFrame([{"amount": 100}])

    # Test: Buffer larger than limit
    with pytest.raises(ValueError, match="Buffer should be less than target limit"):
        AML_System(df, target_limit=5000, buffer=6000)

    # Test: Negative values
    with pytest.raises(ValueError, match="Limits and buffer should be positive values"):
        AML_System(df, target_limit=-100, buffer=10)
