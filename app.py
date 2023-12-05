import streamlit as st

from llama_index.llms import LlamaCPP

# List of models with their corresponding URLs
models = {
    "Zephyr-7B-Beta": {
        "url": "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q4_K_M.gguf",
        "max_new_tokens": 512,
    },
    "Llama2-7B-Chat": {
        "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
        "max_new_tokens": 256,
    },
}

def load_llm(model):
    llm = LlamaCPP(
        model_url=model["url"],
        temperature=0.1,
        max_new_tokens=model["max_new_tokens"],
        context_window=3900,
        generate_kwargs={},
        model_kwargs={"n_gpu_layers": -1},
        verbose=True,
    )

    return llm

def main():
    with st.columns(3)[1]:
        st.header("Welcome to ")
    
    selected_model = st.selectbox("Select LLM Model", list(models.keys()))
    selected_model = models[selected_model]

    start_loading = st.button("Load")
    
    llm = None
    
    if start_loading:
        with st.spinner("Loading LLM..."):
            llm = load_llm(selected_model)
            st.success("LLM loaded successfully!")
    
if __name__ == "__main__":
    main()
