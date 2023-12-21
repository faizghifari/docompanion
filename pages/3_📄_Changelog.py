import streamlit as st
import utils

st.set_page_config(page_title="Changelog - Docompanion", page_icon=":page_facing_up:")

cl_txt = utils.read_mdfile("./CHANGELOG.md")
st.markdown(cl_txt)
