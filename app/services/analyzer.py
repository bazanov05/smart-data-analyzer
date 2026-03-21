import pandas as pd


class AML_System:
    def _is_value_positive(self, value):
        return value > 0

    def __init__(self, transaction_ledger: pd.DataFrame, target_limit=10000, buffer=1000):
        self._df = transaction_ledger

        # convert to pandas TimeStamp
        self._df["timestamp"] = pd.to_datetime(self._df["timestamp"])

        if not self._is_value_positive(target_limit) or not self._is_value_positive(buffer):
            raise ValueError("Limits and buffer should be positive values")
        if buffer >= target_limit:
            raise ValueError("Buffer should be less than target limit")
        self._target_limit = target_limit
        self._buffer = buffer

    def detect_structuring_attempts(self):
        """
        Finds structured transfers
        in range between limit and limit - buffer
        """
        return self._df.loc[((self._df.amount >= self._target_limit - self._buffer) & (self._df.amount < self._target_limit))]

    def identify_unverified_originators(self):
        """
        Finds senders without id
        """
        anonymous_mask = self._df.isnull()
        return self._df.loc[anonymous_mask.sender_id]

    def aggregate_geographic_inflow(self):
        """
        Finds coutries with the biggest inflows
        """
        country_exposure_report = self._df.groupby("country").amount.sum()
        return country_exposure_report.sort_values(ascending=False)

    def detect_high_velocity_transfers(self):
        """
        Finds transactions with a high velocity
        based on one hour gap
        """
        sorted_df = self._df.sort_values(by="timestamp")

        #  we want to check the high velocity based on last 3 transactions
        #  so that is why we shift 2 rows down to compare the 1st one and the 3rd one
        shifted_timestamps = sorted_df.groupby(sorted_df.sender_id)["timestamp"].shift(2)

        #  now i create new col as a result of substracion
        sorted_df['time_gap'] = sorted_df['timestamp'] - shifted_timestamps
        result = sorted_df.loc[sorted_df['time_gap'] <= pd.Timedelta(hours=1)]
        return result
