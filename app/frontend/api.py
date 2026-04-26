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

    def upload_csv(self, file: BytesIO):
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
