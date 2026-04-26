import streamlit as st


st.set_page_config(page_title="AML System", layout="wide")


with st.sidebar:
    st.title("AML Analyzer")
    st.caption("smart-data-analyzer")

    menu = st.radio(
        "Navigation",
        ["Overview", "Structuring", "High velocity", "Geographic", "AI agent"],
        label_visibility="collapsed"
    )

    st.divider()
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    # placeholder for API upload trigger
    if uploaded_file:
        st.success("File ready for analysis")

# handle the navigation logic
match menu:
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
