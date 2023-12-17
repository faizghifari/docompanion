import chromadb
import streamlit as st

from streamlit_extras.switch_page_button import switch_page

from setup_llm import setup_llm_display
from setup_docs import setup_docs_display

st.set_page_config(page_title="Home - Docompanion", page_icon=":blue_book:")


def main():
    if "db" not in st.session_state:
        st.session_state.db = chromadb.PersistentClient(path="./db")
    if "service_context" not in st.session_state:
        st.session_state.service_context = None
    if "model_path" not in st.session_state:
        st.session_state.model_path = None
    if "download_button" not in st.session_state:
        st.session_state.download_button = False
    if "subq_qe_engine" not in st.session_state:
        st.session_state.subq_qe_engine = None
    if "file_paths" not in st.session_state:
        st.session_state.file_paths = []

    st.columns((2.25, 3, 2.25))[1].header(
        "Docompanion :blue_book:", anchor="home", divider="rainbow"
    )

    st.subheader("Setup Your LLM Companion", anchor="llm")

    llm_container = st.empty()
    if st.session_state.service_context is None:
        with llm_container.container():
            setup_llm_display()

    if st.session_state.service_context:
        llm_container.empty()
        st.success("LLM loaded successfully!")
        setup_docs_display()

    if st.session_state.subq_qe_engine and st.session_state.service_context:
        st.write("")
        if st.columns((1, 1, 1))[1].button("Start Your Companion", type="primary"):
            switch_page("chat companion")


if __name__ == "__main__":
    main()
