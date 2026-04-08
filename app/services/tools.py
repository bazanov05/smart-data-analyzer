from langchain_core.tools import tool
from app.db.repository import (
    get_all_structuring_attempts
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
            formatted_attempt = f"id: {attempt.id}, sender_id: {attempt.sender_id}, amount: {attempt.amount}, country: {attempt.country}, created_at: {attempt.created_at}"
            formatted_attempts.append(formatted_attempt)

        # return the string - not the list(Python object)
        return "\n".join(formatted_attempts)

    return fetch_structuring_logs
