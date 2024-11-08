import streamlit as st
from multi_image_processor import MultiImageProcessor  # Only import MultiImageProcessor
from utils import reset_session_state

# Set page configuration
st.set_page_config(page_title="AI-Driven Tool", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a section", ["TestCase Generator"])

# API Key Input
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your API key:", type="password")
if api_key:
    st.session_state["api_key"] = api_key

# Check if the API key is set, if not prompt the user
if "api_key" not in st.session_state:
    st.warning("Please enter your API key to proceed.")
else:
    if page == "TestCase Generator":
        st.title("AI-Driven Test Case Generator")

        # Dropdown to select between data sources
        option = st.selectbox("Choose your data source", ("Multi-Image",), key="option_selector")

        # Reset session state if a new option is selected
        if "last_option" not in st.session_state:
            st.session_state.last_option = option
        elif st.session_state.last_option != option:
            reset_session_state()
            st.session_state.last_option = option

        # Run MultiImageProcessor with the API key from session state
        if option == "Multi-Image":
            MultiImageProcessor(api_key=st.session_state["api_key"]).run()

        # Display response only for TestCase Generator
        if "response" in st.session_state and st.session_state.response:
            st.text_area("Response:", st.session_state.response, height=300, key="displayed_response")
            if st.button("Copy Response"):
                st.code(st.session_state.response, language="")
