import chromadb
import nest_asyncio
import streamlit as st

from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.storage.storage_context import StorageContext
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores import ChromaVectorStore
from llama_index.llms import LlamaCPP

from utils import parse_string

nest_asyncio.apply()

if "db" not in st.session_state:
    st.session_state.db = chromadb.PersistentClient(path="./db")


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
