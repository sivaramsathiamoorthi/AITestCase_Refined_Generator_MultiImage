import streamlit as st
from PIL import Image
from image_info_generator import ImageInfoGenerator
from zipfile import ZipFile
import tempfile
import os
from streamlit_image_select import image_select

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

                # Prepare JPEG-converted images
                jpeg_images = []
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_path = os.path.join(root, file)
                            image = Image.open(image_path)
                            
                            # Convert to JPEG format
                            jpeg_image_path = os.path.join(temp_dir, f"{os.path.splitext(file)[0]}.jpg")
                            rgb_image = image.convert("RGB")  # Ensure image is in RGB mode for JPEG
                            rgb_image.save(jpeg_image_path, format="JPEG")
                            jpeg_images.append(jpeg_image_path)

                if jpeg_images:
                    # Use image_select to display images in a tile format
                    selected_image_path = image_select(
                        label="Select an image:",
                        images=jpeg_images,
                        use_container_width=True
                    )

                    # Show the selected image and provide question input
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
