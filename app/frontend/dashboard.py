import streamlit as st


# catch the users choice in a variable
# radio - because we can click only on one board at a time
page = st.sidebar.radio("Navigation", [
    "Overview",
    "Structuring attempts",
    "High velocity",
    "Geographic inflow",
    "Unverified originators",
    "AI summaries",
    "AI agent",
])


# handle the navigation logic
match page:
    case "Overview":
        st.subheader("System Overview")

    case "Structuring attempts":
        st.subheader("Structuring Analysis")

    case "High velocity":
        st.subheader("High Velocity Transfers")

    case "Geographic inflow":
        st.subheader("Geographic Risk Inflow")

    case "Unverified originators":
        st.subheader("Unverified Originator Reports")

    case "AI summaries":
        st.subheader("Historical AI Insights")

    case "AI agent":
        st.subheader("AI AML Analyst")
