# multi_image_processor.py
import streamlit as st
from multi_image_selector import MultiImageSelector
from PIL import Image
from image_info_generator import ImageInfoGenerator  # Correct import from separate file

class MultiImageProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or st.session_state.get("api_key")
        if not self.api_key:
            st.error("API key is required for generating responses.")
            return

        # Initialize dependencies with the API key
        self.multi_image_selector = MultiImageSelector()
        self.image_generator = ImageInfoGenerator(api_key=self.api_key)

    def run(self):
        if not self.api_key:
            st.warning("Please enter a valid API key in the configuration.")
            return

        folder_path = st.text_input("Enter the folder path containing images:")
        if folder_path:
            images = self.multi_image_selector.load_images_from_folder(folder_path)
            if images:
                selected_image = self.multi_image_selector.display(label="Choose an image:", use_container_width=True)
                if selected_image:
                    st.image(selected_image, caption="Expanded Image View", use_column_width=True)
                    question = st.text_area("Enter your question about the selected image:", height=100)
                    if st.button("Generate Multi-Image Response"):
                        description = self.image_generator.generate_image_description(
                            Image.open(selected_image), question
                        )
                        st.session_state.response = description or "No response generated. Please check your question and try again."
            else:
                st.warning("The folder is empty or no images were found.")
