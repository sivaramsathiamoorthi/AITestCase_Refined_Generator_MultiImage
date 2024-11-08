import streamlit as st
from PIL import Image
from image_info_generator import ImageInfoGenerator
from zipfile import ZipFile
import tempfile
import os

class MultiImageProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or st.session_state.get("api_key")
        if not self.api_key:
            st.error("API key is required for generating responses.")
            return

        self.image_generator = ImageInfoGenerator(api_key=self.api_key)

    def run(self):
        uploaded_file = st.file_uploader("Upload a ZIP file containing images", type=["zip"])
        if uploaded_file:
            with tempfile.TemporaryDirectory() as temp_dir:
                with ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                image_files = []
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_files.append(os.path.join(root, file))
                
                if image_files:
                    # Display images in a grid layout
                    selected_image_path = None
                    cols = st.columns(3)  # Adjust number of columns as needed
                    for i, image_path in enumerate(image_files):
                        with cols[i % 3]:  # Display images in grid format
                            if st.button("Select", key=image_path):
                                selected_image_path = image_path
                            st.image(image_path, use_column_width=True)

                    # Show selected image for further processing
                    if selected_image_path:
                        image = Image.open(selected_image_path)
                        st.image(image, caption="Selected Image", use_column_width=True)
                        
                        question = st.text_area("Enter your question about the selected image:", height=100)
                        if st.button("Generate Multi-Image Response"):
                            description = self.image_generator.generate_image_description(image, question)
                            st.session_state.response = description or "No response generated. Please check your question and try again."
                else:
                    st.warning("The uploaded ZIP file contains no valid image files.")
        else:
            st.info("Please upload a ZIP file containing images to proceed.")
