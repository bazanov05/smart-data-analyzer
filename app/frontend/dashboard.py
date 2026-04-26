import streamlit as st


st.set_page_config(page_title="AML System", layout="wide")


# everything should be placed on the left side
with st.sidebar:
    st.title("AML Analyzer")
    st.caption("smart-data-analyzer")

    # radio because we can click only at one
    menu = st.radio(
        "Navigation",
        [
            "Overview",
            "Structuring attempts",
            "High velocity",
            "Geographic inflow",
            "Unverified originators",
            "AI summaries",
            "AI agent",
        ],
        label_visibility="collapsed"
    )

    st.divider()

    # if file is not uploaded - variable becomes None
    # otherwise - BytesIO object
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])    # type for safety filter

    # placeholder for API upload trigger
    if uploaded_file:
        # immediate feedback for user - green box with chechmark icon
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
