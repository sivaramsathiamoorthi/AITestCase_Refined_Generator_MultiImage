import streamlit as st
from PIL import Image
from image_info_generator import ImageInfoGenerator
from zipfile import ZipFile
import tempfile
import os

class MultiImageProcessor:
    def __init__(self, api_key=None):
        # Fetch or set the API key
        self.api_key = api_key or st.session_state.get("api_key")
        if not self.api_key:
            st.error("API key is required for generating responses.")
            return
        
        # Initialize the image generator with the provided API key
        self.image_generator = ImageInfoGenerator(api_key=self.api_key)

    def run(self):
        # File uploader for a ZIP file of images
        uploaded_file = st.file_uploader("Upload a ZIP file containing images", type=["zip"])
        if uploaded_file:
            # Create a temporary directory for extracted images
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the ZIP file contents to the temporary directory
                with ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Recursively find all image files in the extracted contents
                image_files = []
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_files.append(os.path.join(root, file))
                
                if image_files:
                    # Dropdown for selecting an image from the extracted files
                    selected_image_path = st.selectbox("Select an image:", image_files)
                    if selected_image_path:
                        image = Image.open(selected_image_path)
                        st.image(image, caption="Selected Image", use_column_width=True)
                        
                        # Text area for entering a question about the selected image
                        question = st.text_area("Enter your question about the selected image:", height=100)
                        
                        # Button to generate a response for the selected image
                        if st.button("Generate Multi-Image Response"):
                            description = self.image_generator.generate_image_description(image, question)
                            st.session_state.response = description or "No response generated. Please check your question and try again."
                else:
                    st.warning("The uploaded ZIP file contains no valid image files.")
        else:
            st.info("Please upload a ZIP file containing images to proceed.")
