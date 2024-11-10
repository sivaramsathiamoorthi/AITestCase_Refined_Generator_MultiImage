import streamlit as st
from multi_image_processor import MultiImageProcessor
from web_processor import WebProcessor
from utils import reset_session_state

# Set page configuration
st.set_page_config(page_title="AI-Driven Tool", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a section", ["Content Assitant"])

# API Key Input
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your API key:", type="password")
if api_key:
    st.session_state["api_key"] = api_key

# Check if the API key is set, if not prompt the user
if "api_key" not in st.session_state:
    st.warning("Please enter your API key to proceed.")
else:
    if page == "Content Assitant":
        st.title("AI-Driven Assitant tool")

        # Dropdown to select between data sources
        option = st.selectbox("Choose your data source", ("Multi-Image", "Web Search"), key="option_selector")

        # Reset session state if a new option is selected
        if "last_option" not in st.session_state:
            st.session_state.last_option = option
        elif st.session_state.last_option != option:
            reset_session_state()
            st.session_state.last_option = option

        # Run the selected processor with the API key from session state
        if option == "Multi-Image":
            MultiImageProcessor(api_key=st.session_state["api_key"]).run()
        elif option == "Web Search":
            WebProcessor(api_key=st.session_state["api_key"]).run()

        # Remove the redundant response box code
