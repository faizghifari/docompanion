import os
import re
import glob
import requests
import chromadb
import tempfile

import nest_asyncio
import streamlit as st

from llama_index import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
from llama_index.storage.storage_context import StorageContext
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.vector_stores import ChromaVectorStore
from llama_index.llms import LlamaCPP

nest_asyncio.apply()

supported_files = [
    ".pdf",
    ".csv",
    ".docx",
    ".txt",
    ".epub",
    ".hwp",
    ".mbox",
    ".ppt",
    ".pptm",
    ".pptx",
    ".ipynb",
    ".md",
]
supported_files_txt = "\n".join([f"- {t}" for t in supported_files])

st.set_page_config(page_title="Home - Docompanion", page_icon=":blue_book:")
db = chromadb.PersistentClient(path="./db")


def download(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    filename = url.split("/")[-1].replace(" ", "_")
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        progress_text = "Downloading LLM. Please wait."
        download_bar = st.progress(0.0, text=progress_text)
        total_size = int(r.headers.get("content-length"))
        with open(file_path, "wb") as f:
            print("Downloading %s" % file_path)
            downloaded = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                    downloaded = downloaded + len(chunk)
                    progress = downloaded / total_size
                    download_bar.progress(progress, text=progress_text)

        return file_path
    else:
        raise ConnectionError(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )


def parse_string(input_string):
    parsed_string = input_string.replace(" ", "_")
    parsed_string = parsed_string.replace("-", "_")
    parsed_string = re.sub(r"[^a-z0-9_]", "", parsed_string.lower())
    parsed_string = re.sub(r"(_)\1+", r"\1", parsed_string)

    return parsed_string


def parse_model_fname(input_path):
    return input_path.replace("\\", "/").split("/")[-1]


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


def build_index_and_query_engine(files, service_context):
    query_engine_tools = []
    for file in files:
        new = False
        title = " ".join(file.replace("\\", "/").split("/")[-1].split(".")[:-1])
        collection_name = parse_string(title)[:63]
        try:
            chroma_collection = db.get_collection(collection_name)
        except:
            new = True
            documents = SimpleDirectoryReader(input_files=[file]).load_data()
            chroma_collection = db.create_collection(collection_name)

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        if new:
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                service_context=service_context,
                use_async=True,
            )
        else:
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                service_context=service_context,
                use_async=True,
            )

        query_engine = index.as_query_engine()
        query_engine_tools.append(
            QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=collection_name,
                    description=f"A Paper titled: {title}",
                ),
            )
        )

    return query_engine_tools


def main():
    st.columns((2.25, 3, 2.25))[1].header(
        "Docompanion :blue_book:", anchor="home", divider="rainbow"
    )

    st.subheader("Setup Your LLM Companion", anchor="llm")
    models_path = glob.glob("./llm/*.gguf")

    llm = None
    selected = False
    subq_qe_engine = None

    if models_path:
        st.markdown(
            """Place your existing LLM file at `llm` directory  
            (Only support .gguf filetype for `llama.cpp`)"""
        )
        model_path = st.selectbox(
            "Select Existing LLM Model",
            list(models_path),
            placeholder="Choose a LLM",
            format_func=parse_model_fname,
        )
        selected = True
    else:
        st.markdown(
            """No LLM file found at `llm` directory, provide a URL to a LLM model file to download  
            (Only support .gguf filetype for `llama.cpp`)"""
        )
        model_url = st.text_input(
            "Model URL",
            "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q4_K_M.gguf",
        )
        if st.button("Download LLM"):
            model_path = download(model_url, "./llm/")
            st.success(f"LLM downloaded and placed at {model_path}")
            selected = True

    if selected:
        if st.button("Load LLM"):
            with st.spinner("Loading LLM..."):
                llm = load_llm(model_path)
                st.success("LLM loaded successfully!")
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    )

    st.subheader("Provide Your Docs", anchor="docs")
    uploaded_files = st.file_uploader(
        "Upload documents to be stored and indexed",
        accept_multiple_files=True,
        type=[
            "pdf",
            "csv",
            "docx",
            "txt",
            "epub",
            "hwp",
            "mbox",
            "ppt",
            "pptm",
            "pptx",
            "ipynb",
            "md",
        ],
    )

    if uploaded_files:
        file_paths = []
        temp_dir = tempfile.mkdtemp()
        for file in uploaded_files:
            path = os.path.join(temp_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.getvalue())
            file_paths.append(path)

        subq_qe_engine = build_index_and_query_engine(file_paths, service_context)
        st.success("Documents Index and Query Engine built successfully!")

    if subq_qe_engine:
        st.write("")
        if st.columns((1, 1, 1))[1].button("Start Your Companion", type="primary"):
            st.experimental_set_query_params(page="new_page")


if __name__ == "__main__":
    main()
