from langchain_core.tools import tool
from sqlalchemy.orm import Session
from app.db.repository import (
    get_all_structuring_attempts,
    get_all_geographical_inflows,
    get_all_high_velocity_transfers
)


def get_structuring_tool(db_session):
    """
    Outer function which provides db session to our tool
    as agent himself cannot access our db and
    tool cannot receive db session as an argument
    """

    @tool
    def fetch_structuring_logs() -> str:
        """
        Fetches all structuring attempts from the database.
        Structuring is when a user breaks down a large transaction into smaller
        transactions to avoid regulatory reporting thresholds.
        Use this tool whenever the user asks about structuring risks,
        divided payments, or attempts to bypass limits.
        """

        attempts = get_all_structuring_attempts(db=db_session)

        if not attempts:
            return "No structuring attempts found in the database."

        # agent undestands only strings so we iterate through
        # db objects and return the formatted string
        formatted_attempts = []
        for attempt in attempts:
            formatted_attempt = (
                f"id: {attempt.id}, "
                f"transaction_id: {attempt.transaction_id}, "
                f"sender_id: {attempt.sender_id}, "
                f"receiver_id: {attempt.receiver_id}, "
                f"amount: {attempt.amount}, "
                f"summed_amount: {attempt.summed_amount}, "
                f"country: {attempt.country}, "
                f"timestamp: {attempt.timestamp}, "
                f"created_at: {attempt.created_at}"
                )

            formatted_attempts.append(formatted_attempt)

        # return the string - not the list(Python object)
        return "\n".join(formatted_attempts)

    return fetch_structuring_logs


def get_geographical_inflow_tool(db_session: Session):
    """
    Outer function which provides db session to our tool
    """

    @tool
    def fetch_geo_inflow_logs() -> str:
        """
        Fetches transactions from high-risk or unusual geographic regions.
        Use this tool whenever the user asks about cross-border risks,
        international transfers, or geographic anomalies.
        """
        attempts = get_all_geographical_inflows(db_session)

        if not attempts:
            return "No geographical inflow info found in the database."

        formatted_attempts = []

        for attempt in attempts:
            formatted_attempt = (
                f"id: {attempt.id}, "
                f"country: {attempt.country}, "
                f"inflow: {attempt.inflow}, "
                f"risk_level: {attempt.risk_level}, "
                f"created_at: {attempt.created_at}"
                )

            formatted_attempts.append(formatted_attempt)

        return "\n".join(formatted_attempts)

    return fetch_geo_inflow_logs


def get_high_velocity_transfers_tool(db_session: Session):
    """
    Outer function which provides db session to our tool
    """
    @tool
    def fetch_high_velocity_transfers_logs() -> str:
        """
        Fetches accounts moving money rapidly (layering).
        Use this tool whenever the user asks about rapid movement,
        high volume, bursts of activity, or layering.
        """
        attempts = get_all_high_velocity_transfers(db=db_session)

        if not attempts:
            return "No high velocity transfers were found in the database."

        formatted_attempts = []
        for attempt in attempts:
            formatted_attempt = (
                f"id: {attempt.id}, "
                f"transaction_id: {attempt.transaction_id}, "
                f"sender_id: {attempt.sender_id}, "
                f"receiver_id: {attempt.receiver_id}, "
                f"amount: {attempt.amount}, "
                f"frequency: {attempt.frequency}, "
                f"time_gap: {attempt.time_gap}, "
                f"country: {attempt.country}, "
                f"timestamp: {attempt.timestamp}, "
                f"created_at: {attempt.created_at}"
            )
            formatted_attempts.append(formatted_attempt)

        return "\n".join(formatted_attempts)

    return fetch_high_velocity_transfers_logs
