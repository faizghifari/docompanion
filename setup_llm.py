import glob
import streamlit as st

from llama_index.llms import LlamaCPP
from llama_index import ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding

import utils


def load_llm(model_path):
    llm = LlamaCPP(
        model_path=model_path,
        temperature=0.1,
        max_new_tokens=256,
        context_window=3900,
        generate_kwargs={},
        model_kwargs={"n_gpu_layers": -1},
        verbose=True,
    )

    return llm


def container_select_llm(models_path):
    st.markdown(
        """Place your existing LLM file at `llm` directory  
        (Only support .gguf filetype for `llama.cpp`)"""
    )
    st.session_state.model_path = st.selectbox(
        "Select Existing LLM Model",
        list(models_path),
        placeholder="Choose a LLM",
        format_func=utils.parse_model_fname,
    )


def container_download_llm():
    st.markdown(
        """No LLM file found at `llm` directory, provide a URL to a LLM model file to download  
        (Only support .gguf filetype for `llama.cpp`)"""
    )
    model_url = st.text_input(
        "Model URL",
        "https://huggingface.co/TheBloke/stablelm-zephyr-3b-GGUF/resolve/main/stablelm-zephyr-3b.Q4_K_M.gguf",
    )

    return model_url


def setup_service_context():
    with st.columns((1, 0.7, 1))[1]:
        with st.spinner("Loading LLM..."):
            llm = load_llm(st.session_state.model_path)
            st.session_state.service_context = ServiceContext.from_defaults(
                llm=llm,
                embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
            )


def setup_llm_display():
    models_path = glob.glob("./llm/*.gguf")
    if models_path:
        container_select_llm(models_path)
    else:
        model_url = container_download_llm()

        if st.columns((1, 0.5, 1))[1].button(
            "Download LLM", disabled=st.session_state.download_button
        ):
            st.session_state.download_button = True
            st.session_state.model_path = utils.download(model_url, "./llm/")
            st.success(f"LLM downloaded and placed at {st.session_state.model_path}")
            st.rerun()

    if st.session_state.model_path is not None:
        if st.columns((1, 0.5, 1))[1].button("Load LLM"):
            setup_service_context()
