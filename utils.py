import streamlit as st

def reset_session_state():
    st.session_state.pop("response", None)
    st.session_state.pop("image_description", None)
    st.session_state.pop("vector_store", None)
    st.session_state.pop("web_data_loaded", None)  # Reset web data load state
