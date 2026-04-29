from app.frontend.api import AMLApiClient
import streamlit as st
import plotly.express as px
import pandas as pd


def _get_fetched_data(data_to_get: str, get_function) -> dict:
    if data_to_get not in st.session_state:
        fetched_data = get_function()
        st.session_state[data_to_get] = fetched_data
    return st.session_state[data_to_get]


def show_overview_page(api: AMLApiClient):
    structuring_data = _get_fetched_data("structuring_attempts", api.get_structuring_attempts)
    high_velocity_data = _get_fetched_data("high_velocity", api.get_high_velocity_transfers)
    geo_inflow_data = _get_fetched_data("geo_inflow", api.get_geographical_inflows)
    unverified_users_data = _get_fetched_data("unverified_users", api.get_unverified_originators)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Structuring flags", len(structuring_data))
    col2.metric("High velocity", len(high_velocity_data))
    col3.metric("Unverified originators", len(unverified_users_data))
    col4.metric(
        "High risk countries",
        sum(1 for d in geo_inflow_data if d.get("risk_level") == "High-risk")
    )

    st.divider()

    st.subheader("Geographic Inflow")
    if geo_inflow_data:
        # convert to DataFrame so Plotly can work with it
        df = pd.DataFrame(geo_inflow_data)

        # sort by inflow so biggest bar is at the top
        df = df.sort_values("inflow", ascending=False).head(10) # show only top 10
        df = df.sort_values("inflow", ascending=True)  # flip for horizontal display

        # map risk level to color — red for high risk, blue for low risk
        color_map = {"High-risk": "#E24B4A", "Low-risk": "#378ADD"}

        fig = px.bar(
            df,
            x="inflow",           # bar length = inflow amount
            y="country",          # each country gets its own bar
            orientation="h",      # horizontal bars
            color="risk_level",   # color each bar by risk level
            color_discrete_map=color_map,
            text="inflow",        # show the value on the bar
            labels={"inflow": "Total Inflow ($)", "country": "Country", "risk_level": "Risk Level"}
        )

        # format the text labels on bars as dollar amounts
        fig.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")

        # clean up the chart background to match Streamlit's theme
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            height=400,
            margin=dict(l=0, r=40, t=20, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Recent Flags")
    all_flags = structuring_data + high_velocity_data
    # sort by data - "timestamp"
    recent = sorted(all_flags, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
    if recent:
        display_cols = ["sender_id", "amount", "country", "type"]
        recent_display = [{k: r[k] for k in display_cols if k in r} for r in recent]
        st.dataframe(recent_display, use_container_width=True)
    else:
        st.info("No recent flags. Upload a CSV to generate reports.")
