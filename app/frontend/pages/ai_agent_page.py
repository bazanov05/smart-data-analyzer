from app.frontend.api import AMLApiClient
import streamlit as st


def show_ai_agent_chat_page(api: AMLApiClient):
    # if the chat is empty - create a empty list od dict's
    # to save and show the chat history
    if "ai_agent_chat" not in st.session_state:
        st.session_state["ai_agent_chat"] = []

    # showing the previous messages
    for data in st.session_state["ai_agent_chat"]:
        with st.chat_message(data["role"]):
            st.write(data["content"])

    # capture present input
    question = st.chat_input("Ask about suspicious activity...")

    # if it is not empty - show it, save to history and trigger the ai agent
    if question:
        st.session_state["ai_agent_chat"].append({
            "role": "user",
            "content": question
        })
        with st.chat_message("user"):
            st.write(question)

        # make a spinner what API is blocked for a sec
        with st.spinner("AI is analyzing your question..."):
            ai_agent_response = api.trigger_the_agent(question)

        # extract data safely
        summary = ai_agent_response.get("summary", "Error: No response from AI.")
        risk_score = ai_agent_response.get("risk_score", 0)

        # format the final output to look professional
        final_response = f"{summary}\n\n**Assigned Risk Score:** {risk_score}/10"

        # save and show AI message
        st.session_state["ai_agent_chat"].append({
            "role": "ai",
            "content": final_response
        })
        with st.chat_message("ai"):
            st.write(final_response)
