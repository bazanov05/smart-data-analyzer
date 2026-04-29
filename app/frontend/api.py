import requests
from io import BytesIO


BASE_URL = "http://localhost:8000"


class AMLApiClient:
    """
    Client to interact with the AML FastAPI backend.
    Uses a persistent session to optimize connection performance.
    """
    def __init__(self):
        """Initializes the base URL and a shared requests Session."""
        self._url = BASE_URL

        # Session allows to reuse the connection, keeps it open
        self._session = requests.Session()

    def upload_csv(self, file: BytesIO) -> dict | None:
        """
        Sends a CSV file to the backend /update endpoint for AML analysis.
        Returns dict if the analysis was successful,
        otherwise returns None if the server was unreachable or an error appeared
        """
        files = {"file": ("filename.csv", file, "text/csv")}
        try:
            response = self._session.post(f"{self._url}/update", files=files)

            # trigger the except block if status is 4xx or 5xx
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None     # server is unreachable

    def get_structuring_attempts(self) -> list:
        """
        Fetches all structuring attempt reports.
        Calls the backend route and returns a list of records for the dashboard table.
        """
        try:
            response = self._session.get(f"{self._url}/reports/structuring_attempts")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_unverified_originators(self) -> list:
        """
        Fetches all unverified originator reports.
        Calls the backend route and returns a list of records for the dashboard table.
        """
        try:
            response = self._session.get(f"{self._url}/reports/unverified_originators")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_geographical_inflows(self) -> list:
        """
        Fetches all geographical inflow reports.
        Calls the backend route and returns a list of records for the dashboard table.
        """
        try:
            response = self._session.get(f"{self._url}/reports/geographical_inflows")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_high_velocity_transfers(self) -> list:
        """
        Fetches all high velocity transfer reports.
        Calls the backend route and returns a list of records for the dashboard table.
        """
        try:
            response = self._session.get(f"{self._url}/reports/high_velocity_transfers")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_raw_data(self) -> list:
        """
        Fetches all raw transaction data.
        Calls the backend route and returns a list of the original transaction records.
        """
        try:
            response = self._session.get(f"{self._url}/reports/raw_data")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_ai_summaries(self) -> list:
        """
        Fetches all historical AI summaries.
        Calls the backend route and returns a list of previously generated AI insights.
        """
        try:
            response = self._session.get(f"{self._url}/reports/ai_summaries")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_structuring_attempt_by_id(self, report_id: int) -> dict:
        """
        Fetches a single structuring attempt report by ID.
        Returns a dictionary with the report details, or an empty dict if not found.
        """
        try:
            response = self._session.get(f"{self._url}/reports/structuring_attempt/{report_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}

    def get_unverified_originator_by_id(self, report_id: int) -> dict:
        """
        Fetches a single unverified originator report by ID.
        Returns a dictionary with the report details, or an empty dict if not found.
        """
        try:
            response = self._session.get(f"{self._url}/reports/unverified_originator/{report_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}

    def get_geographical_inflow_by_id(self, report_id: int) -> dict:
        """
        Fetches a single geographical inflow report by ID.
        Returns a dictionary with the report details, or an empty dict if not found.
        """
        try:
            response = self._session.get(f"{self._url}/reports/geographical_inflow/{report_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}

    def get_high_velocity_transfer_by_id(self, report_id: int) -> dict:
        """
        Fetches a single high velocity transfer report by ID.
        Returns a dictionary with the report details, or an empty dict if not found.
        """
        try:
            response = self._session.get(f"{self._url}/reports/high_velocity_transfer/{report_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}

    def get_raw_data_by_id(self, report_id: int) -> dict:
        """
        Fetches a single raw data report by ID.
        Returns a dictionary with the report details, or an empty dict if not found.
        """
        try:
            response = self._session.get(f"{self._url}/reports/raw_data/{report_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}

    def trigger_the_agent(self, question: str) -> dict:
        """
        Triggers the ai agent.
        Returns a dictionary with the report details,
        such as summary, risk_score and reasoning
        or an empty dict if not found.
        """
        try:
            # send the question as json payload
            response = self._session.post(f"{self._url}/analyze", json={"question": question})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}
