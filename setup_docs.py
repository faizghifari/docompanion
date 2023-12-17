import os

import tempfile
import nest_asyncio
import streamlit as st

from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.storage.storage_context import StorageContext
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores import ChromaVectorStore

import utils

nest_asyncio.apply()


def build_index_and_query_engine(files, service_context):
    query_engine_tools = []
    for file in files:
        new = False
        title = " ".join(file.replace("\\", "/").split("/")[-1].split(".")[:-1])
        collection_name = utils.parse_string(title)[:63]
        try:
            chroma_collection = st.session_state.db.get_collection(collection_name)
        except:
            new = True
            documents = SimpleDirectoryReader(input_files=[file]).load_data()
            chroma_collection = st.session_state.db.create_collection(collection_name)

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


def setup_upload_files():
    uploaded_files = st.file_uploader(
        "Upload documents to be stored and indexed",
        accept_multiple_files=True,
        type=utils.get_supported_files(),
    )

    if uploaded_files:
        temp_dir = tempfile.mkdtemp()
        for file in uploaded_files:
            path = os.path.join(temp_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.getvalue())
            st.session_state.file_paths.append(path)


def setup_docs_display():
    st.subheader("Provide Your Docs", anchor="docs")

    docs_container = st.empty()
    if st.session_state.subq_qe_engine is None:
        with docs_container.container():
            setup_upload_files()

            if len(st.session_state.file_paths) > 0:
                if st.columns((1, 1, 1))[1].button("Build Document Index"):
                    with st.spinner("Indexing..."):
                        st.session_state.subq_qe_engine = build_index_and_query_engine(
                            st.session_state.file_paths,
                            st.session_state.service_context,
                        )

    if st.session_state.subq_qe_engine:
        docs_container.empty()
        st.success("Document Index and Query Engine built successfully!")
