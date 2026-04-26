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


def show_structuring_page(api: AMLApiClient):

    # to avoid an API call if the data is already stored
    if "structuring_attempts" not in st.session_state:
        fetched_data = api.get_structuring_attempts()

        st.session_state["structuring_attempts"] = fetched_data

    data = st.session_state["structuring_attempts"]

    # handle empty state
    if not data:
        st.info("No structuring attempts found. Upload a CSV first.")
        st.stop()   # to prevent the rest of a code

    # divide the page into three equal columns to show breaf sum up
    total_flags, highest_summed_amount, most_common_country = st.columns(3)

    total_flags.metric("Total flags", len(data))
    highest_summed_amount.metric("Highest summed amount", max([d["summed_amount"] for d in data]))
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
            details = api.get_structuring_attempt_by_id(report_id)

            if details:
                st.write(details)
            else:
                st.info("Could not retrieve details for this report.")
