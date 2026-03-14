import pandas as pd


class AML_System:
    def _is_value_positive(self, value):
        return value > 0

    def __init__(self, transaction_ledger: pd.DataFrame, target_limit=10000, buffer=1000):
        self._df = transaction_ledger
        if not self._is_value_positive(target_limit) or not self._is_value_positive(buffer):
            raise ValueError("Limits and buffer should be positive values")
        if buffer >= target_limit:
            raise ValueError("Buffer should be less than target limit")
        self._target_limit = target_limit
        self._buffer = buffer

    def detect_structuring_attempts(self):
        return self._df.loc[((self._df.amount >= self._target_limit - self._buffer) & (self._df.amount < self._target_limit))]

    def identify_unverified_originators(self):
        anonymous_mask = self._df.isnull()
        return self._df.loc[anonymous_mask.sender_id]

    def aggregate_geographic_inflow(self):
        country_exposure_report = self._df.groupby("country").amount.sum()
        return country_exposure_report.sort_values(ascending=False)
