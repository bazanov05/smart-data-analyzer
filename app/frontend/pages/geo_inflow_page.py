from app.frontend.api import AMLApiClient
import streamlit as st
import pandas as pd


def _find_highest_inflow_country(aml_data: list) -> str:
    """
    Finds the dictionary with the highest inflow,
    then extracts the country name.
    """
    if not aml_data:
        return "N/A"
    highest_record = max(aml_data, key=lambda d: d["inflow"])
    return highest_record["country"]


def _count_the_high_risk(data: list) -> int:
    """
    Iterates through the list directly and
    returns the count of high-risk inflows.
    """
    return sum(1 for d in data if d.get("risk_level") == "High-risk")


def show_geo_inflow_page(api: AMLApiClient):

    # to avoid an API call if the data is already stored
    if "geo_inflow" not in st.session_state:
        fetched_data = api.get_geographical_inflows()

        st.session_state["geo_inflow"] = fetched_data

    data = st.session_state["geo_inflow"]

    # handle empty state
    if not data:
        st.info("No geographical inflow found. Upload a CSV first.")
        st.stop()   # to prevent the rest of a code

    # divide the page into three equal columns to show breaf sum up
    total_countries, high_risk_count, highest_inflow_country = st.columns(3)

    total_countries.metric("Total countries", len(data))
    high_risk_count.metric("High risk count", _count_the_high_risk(data))
    highest_inflow_country.metric("Highest inflow country", _find_highest_inflow_country(data))

    st.divider()

    st.subheader("Chart of all countries and their inflow")
    df = pd.DataFrame(data)

    # pass the column names as strings
    st.bar_chart(df, x="country", y="inflow", x_label="Countries", y_label="Total inflows")

    st.divider()

    st.error("High-risk countries")

    df_high_inflow = df.loc[df["risk_level"] == "High-risk"]

    # use df_high_inflow as the main dataset, and strings for x/y
    st.bar_chart(
            df_high_inflow, x="country", y="inflow",
            x_label="Countries with high inflow",
            y_label="Total inflows"
    )
