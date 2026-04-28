from app.frontend.api import AMLApiClient
import streamlit as st
import pandas as pd


def show_ai_sum_page(api: AMLApiClient):

    # to avoid an API call if the data is already stored
    if "ai_sum" not in st.session_state:
        fetched_data = api.get_ai_summaries()

        st.session_state["ai_sum"] = fetched_data

    data = st.session_state["ai_sum"]

    # handle empty state
    if not data:
        st.info("No AI summaries found. Upload a CSV first.")
        st.stop()   # to prevent the rest of a code

    st.metric("Total AI Insights", len(data))

    st.divider()

    df = pd.DataFrame(data)
    df_counts = df.groupby("type")["id"].count().reset_index(name="total")
    st.bar_chart(
        df_counts, x="type", y="total",
        x_label="Type of crime", y_label="Total flags"
    )

    # save df to variable to track user's choices
    event = st.dataframe(
        data=data,
        use_container_width=True,
        on_select="rerun",      # allows user to choose the row
        selection_mode="single-row"     # only one row can be chosen
    )

    st.divider()

    if len(event.selection.rows) > 0:
        selected_index = event.selection.rows[0]
        details = data[selected_index]
        summary_id = details["id"]

        st.subheader(f"Detail Analysis: AI Insight #{summary_id}")

        with st.expander("Insight Deep-Dive", expanded=True):
            if details:
                st.write("**AI Analysis Summary**")
                st.info(details.get("summary", "No content available."))

                left_col, right_col = st.columns(2)

                with left_col:
                    st.write("**Insight Info**")
                    st.metric("Insight ID", summary_id)
                    st.metric("Category", details.get("type", "N/A").replace("_", " ").title())

                with right_col:
                    st.write("**Metadata**")
                    rel_report_id = details.get("report_id")
                    st.metric("Related Report ID", rel_report_id if rel_report_id is not None else "General")

                    ts = details.get("created_at", "N/A")
                    readable_ts = str(ts).split(".")[0].replace("T", " ") if "T" in str(ts) else ts
                    st.metric("Generated At", readable_ts)

            else:
                st.error("Could not retrieve details for this insight.")
