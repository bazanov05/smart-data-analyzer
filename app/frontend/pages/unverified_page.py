from app.frontend.api import AMLApiClient
import streamlit as st


def _find_most_common_country(aml_data: dict) -> str:
    frequencies = dict()
    for data in aml_data:
        if data["country"] not in frequencies:
            frequencies[data["country"]] = 1
        else:
            frequencies[data["country"]] += 1
    max_frequency = 0
    most_common_country = ""
    for country, freq in frequencies.items():
        if freq > max_frequency:
            max_frequency = freq
            most_common_country = country
    return most_common_country


def show_unverified_users_page(api: AMLApiClient):

    # to avoid an API call if the data is already stored
    if "unverified_users" not in st.session_state:
        fetched_data = api.get_unverified_originators()

        st.session_state["unverified_users"] = fetched_data

    data = st.session_state["unverified_users"]

    # handle empty state
    if not data:
        st.info("No unverified originators found. Upload a CSV first.")
        st.stop()   # to prevent the rest of a code

    # divide the page into three equal columns to show breaf sum up
    total_flags, total_amount, most_common_country = st.columns(3)

    total_flags.metric("Total flags", len(data))
    total_amount.metric("Total amount sent", f"${sum([d['amount'] for d in data]):,.2f}")
    most_common_country.metric("Most common country", _find_most_common_country(data))

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
            details = api.get_unverified_originator_by_id(report_id)

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

                    # Handle potential "None" string from the backend fix
                    sender = details.get("sender_id", "Unknown")
                    if sender == "None" or not sender:
                        sender = "Unknown"

                    st.metric("Sender ID", sender)
                    st.metric("Receiver ID", details.get("receiver_id", "N/A"))
                    st.metric("Country", details.get("country", "N/A"))

                    # Replaced frequency with num_of_transactions
                    num_txs = details.get("num_of_transactions")
                    if num_txs is not None:
                        st.metric("Total Transactions", num_txs)
                        if num_txs == 1:
                            st.warning("No historical footprint — treating as unverified entity.")
            else:
                st.info("Could not retrieve details for this report.")
