import pandas as pd


class AML_System:
    def __init__(self, transaction_ledger: pd.DataFrame):
        self._df = transaction_ledger

    def detect_structuring_attempts(self):
        return self._df.loc[((self._df.amount >= 9000) & (self._df.amount <= 9999))]

    def identify_unverified_originators(self):
        anonymous_mask = self._df.isnull()
        return self._df.loc[anonymous_mask.sender_id]

    def aggregate_geographic_inflow(self):
        country_exposure_report = self._df.groupby("country").amount.sum()
        return country_exposure_report.sort_values(ascending=False)
