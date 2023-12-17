import time
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Chat - Docompanion", page_icon=":speech_balloon:")

if (
    "service_context" not in st.session_state
    or not st.session_state.service_context
    or "subq_qe_engine" not in st.session_state
    or not st.session_state.subq_qe_engine
    or "file_paths" not in st.session_state
    or not st.session_state.file_paths
):
    switch_page("home")

st.title("Chat with Your Docompanion")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask your docompanion anything about your docs!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = st.session_state.subq_qe_engine.query(prompt)

        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
