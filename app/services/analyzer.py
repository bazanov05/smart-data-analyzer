import pandas as pd
from datetime import timedelta
import numpy as np

HIGH_RISK = {'IR', 'KP', 'SY', 'RU', 'BLR'}


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
        Sums total transaction amounts per country
        and flags high-risk jurisdictions.
        """
        # Sum amounts by country and convert the resulting Series to a DataFrame
        # to keep 'country' as a column, not a key
        report = self._df.groupby("country")["amount"].sum().reset_index()

        # Vectorized check: if country is in HIGH_RISK, label as High-risk, else Low-risk
        report["risk_level"] = np.where(
            report['country'].isin(HIGH_RISK),
            "High-risk",
            "Low-risk"
        )

        # rename a column to match my DB/Schemas
        report = report.rename(columns={'amount': 'inflow'})

        return report

    def detect_high_velocity_transfers(self, time_window: timedelta, frequency_limit: int):
        """
        Identifies senders performing an unusually high
        number of transactions within a rolling time window
        """
        # Pandas operates only with sorted time with rollnig()
        sorted_df = self._df.sort_values(by="timestamp")
        grouped_df = sorted_df.groupby("sender_id")

        # Count the number of transactions for each sender within the sliding time window.
        # As the window moves, transactions older than 'time_window' are excluded from the count.
        rolling_count = grouped_df.rolling(window=time_window, on='timestamp')['amount'].count()
        # Groupby.rolling returns a MultiIndex (sender_id, row_index).
        # Dropping the sender_id level (level 0) aligns the Series back to the original row index.
        sorted_df['frequency'] = rolling_count.reset_index(level=0, drop=True)

        return sorted_df.loc[sorted_df['frequency'] >= frequency_limit]
