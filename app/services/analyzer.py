import pandas as pd
from datetime import timedelta


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

    def detect_structuring_attempts(self, time_window: timedelta):
        """
        Identifies potential structuring by calculating rolling cumulative transaction
        amounts per sender within a specific time window.
        """

        # Pandas operates only with sorted time with rollnig()
        sorted_df = self._df.sort_values(by="timestamp")

        grouped = sorted_df.groupby("sender_id")

        # for every transaction pandas goes back for our time_widnow
        # and summarise the amount of money for this period of time
        # for new row oldest trans gets dropped and the new one is added for each sender
        rolling_sum = grouped.rolling(window=time_window, on="timestamp")['amount'].sum()

        # The groupby operation creates a MultiIndex (sender_id, row_index).
        # to add a new Series we need to drop the first part of address
        sorted_df['summed_amount'] = rolling_sum.reset_index(level=0, drop=True)

        # Filter for cases where the cumulative total falls within the suspicious buffer
        # range just below the reporting limit.
        return sorted_df.loc[
            (sorted_df["summed_amount"] < self._target_limit) &
            (sorted_df["summed_amount"] >= self._target_limit - self._buffer)
        ]

    def identify_unverified_originators(self):
        """
        Flags users with only one transaction in the system.
        These are treated as 'unverified' because they have no history.
        """
        grouped_df = self._df.copy()

        # use transfrom() instead of count() not to collapse data
        # the result of count will be added to every row
        # we want to save all transaction data not only sender_id
        grouped_df['num_of_transactions'] = self._df.groupby("sender_id")["sender_id"].transform("count")

        return grouped_df.loc[grouped_df['num_of_transactions'] == 1]

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
        result['time_gap'] = result['time_gap'].astype(str)
        return result
