from app.frontend.api import AMLApiClient
import streamlit as st


def _find_highest_frequency(aml_data: dict) -> int:
    return max([data["frequency"] for data in aml_data])


def _find_most_common_time_gap(aml_data: dict) -> str:
    frequencies = dict()
    for data in aml_data:
        if data["time_gap"] not in frequencies:
            frequencies[data["time_gap"]] = 1
        else:
            frequencies[data["time_gap"]] += 1
    max_frequency = 0
    most_common_gap = "N/A"
    for gap, freq in frequencies.items():
        if freq > max_frequency:
            max_frequency = freq
            most_common_gap = gap
    return most_common_gap


def show_high_velocity_page(api: AMLApiClient):

    # to avoid an API call if the data is already stored
    if "high_velocity" not in st.session_state:
        fetched_data = api.get_high_velocity_transfers()

        st.session_state["high_velocity"] = fetched_data

    data = st.session_state["high_velocity"]

    # handle empty state
    if not data:
        st.info("No high velocity transfers found. Upload a CSV first.")
        st.stop()   # to prevent the rest of a code

    # divide the page into three equal columns to show breaf sum up
    total_flags, highest_freq, most_common_gap = st.columns(3)

    total_flags.metric("Total flags", len(data))
    highest_freq.metric("Highest frequency", _find_highest_frequency(data))
    most_common_gap.metric("Most common time gap", _find_most_common_time_gap(data))

    st.divider()

    # save df to variable to track user's choices
    event = st.dataframe(
        data=data,
        use_container_width=True,
        on_select="rerun",      # allows user to choose the row
        selection_mode="single-row"     # only one row can be chosen
    )

    # if the user has chosen the row get the info about this attempt
    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        report_id = data[selected_index]["id"]

        st.subheader(f"Detail Analysis: Report #{report_id}")

        # expanded = True - user does not to click to open the data
        # it will be provided automatically
        with st.expander("Investigation Deep-Dive", expanded=True):
            # Fetch the specific report details from the backend
            details = api.get_high_velocity_transfer_by_id(report_id)

            if details:
                left_col, right_col = st.columns(2)

                with left_col:
                    st.write("**Transaction Info**")
                    st.metric("Transaction ID", details.get("transaction_id", "N/A"))
                    st.metric("Amount", f"${details.get('amount', 0):,.2f}")
                    st.metric("Type", details.get("type", "N/A").replace("_", " ").title())

                    # format timestamp to be more readable (YYYY-MM-DD HH:MM)
                    ts = details.get("timestamp", "N/A")
                    readable_ts = ts.split(".")[0].replace("T", " ") if "T" in str(ts) else ts
                    st.metric("Timestamp", readable_ts)

                with right_col:
                    st.write("**Entity & Risk Info**")
                    st.metric("Sender ID", details.get("sender_id", "N/A"))
                    st.metric("Receiver ID", details.get("receiver_id", "N/A"))
                    st.metric("Country", details.get("country", "N/A"))

                    # Replaced summed_amount with frequency
                    frequency = details.get("frequency")
                    if frequency is not None:
                        st.metric("Transfer Frequency", frequency)
                        if frequency >= 5:
                            st.warning("High frequency activity — potential layering detected")
            else:
                st.info("Could not retrieve details for this report.")
