import os
import sys
import time
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import get_random_wait_txt, get_random_answer_txt

st.set_page_config(page_title="Chat - Docompanion", page_icon=":speech_balloon:")


def write_assistant_msg(msg):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        message_placeholder.markdown("▌")
        time.sleep(1)

        for chunk in msg.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})


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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your docompanion anything about your docs!"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    wait_txt = get_random_wait_txt()
    write_assistant_msg(wait_txt)

    assistant_response = st.session_state.subq_qe_engine.query(prompt)
    sub_responses = [
        node.text.replace("Response", "Answer")
        for node in assistant_response.source_nodes
        if node.metadata == {}
    ]
    final_response = "Final Answer:\n\n" + assistant_response.response
    intro_reply = get_random_answer_txt(len(sub_responses))

    all_responses = [intro_reply]
    all_responses.extend(sub_responses)
    all_responses.append(final_response)

    for resp in all_responses:
        write_assistant_msg(resp)
