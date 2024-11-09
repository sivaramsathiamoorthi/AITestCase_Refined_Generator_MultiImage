import streamlit as st
from PIL import Image, ImageGrab
from image_info_generator import ImageInfoGenerator
from zipfile import ZipFile
import tempfile
import os
from streamlit_image_select import image_select
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document

class MultiImageProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or st.session_state.get("api_key")
        if not self.api_key:
            st.error("API key is required for generating responses.")
            return

        self.image_generator = ImageInfoGenerator(api_key=self.api_key)

    def run(self):
        # Initialize session state for response and separate lists for ZIP and clipboard images
        if "response" not in st.session_state:
            st.session_state.response = ""
        if "zip_images" not in st.session_state:
            st.session_state.zip_images = []
        if "clipboard_images" not in st.session_state:
            st.session_state.clipboard_images = []

        # Button to check clipboard for images
        if st.button("Check Clipboard for Image", help="Click to paste an image from the clipboard"):
            self.check_for_pasted_image()

        # File upload for ZIP containing images
        uploaded_file = st.file_uploader("Upload a ZIP file containing images", type=["zip"])
        if uploaded_file:
            self.extract_images_from_zip(uploaded_file)

        # Combine ZIP and clipboard images without duplicates for display in the grid
        combined_images = st.session_state.zip_images + st.session_state.clipboard_images
        if combined_images:
            selected_image = image_select(
                label="Select an image:",
                images=combined_images,
                use_container_width=True
            )

            # Show the selected image and provide question input
            if selected_image:
                image = selected_image
                st.image(image, caption="Selected Image", use_column_width=True)

                question = st.text_area("Enter your question about the selected image:", height=100)
                if st.button("Generate Multi-Image Response"):
                    description = self.image_generator.generate_image_description(image, question)
                    st.session_state.response = description or "No response generated. Please check your question and try again."

        # Display the response in an enhanced format and add the Copy to Clipboard button
        if st.session_state.response:
            st.markdown("### Generated Response:")

            # Enhanced formatting of response with JavaScript Copy to Clipboard button
            st.markdown("""
                <button onclick="navigator.clipboard.writeText(document.getElementById('generated-response').innerText)">
                    Copy to Clipboard
                </button>
                <style>
                    button {
                        background-color: #4CAF50; /* Green */
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 14px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 4px;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Format the response and include it in a scrollable div with an ID for copying
            formatted_response = self.format_response(st.session_state.response)
            st.markdown(f"""
                <div id="generated-response" style="
                    background-color: #f0f4f8; padding: 20px; border-radius: 8px; border: 1px solid #ddd;
                    font-family: Arial, sans-serif; color: #333; max-height: 300px; overflow-y: scroll;">
                    {formatted_response}
                </div>
            """, unsafe_allow_html=True)

            # Download buttons for PDF and Word document
            col1, col2 = st.columns(2)
            with col1:
                pdf_data = self.generate_pdf(st.session_state.response)
                st.download_button(
                    label="Download as PDF",
                    data=pdf_data,
                    file_name="response.pdf",
                    mime="application/pdf"
                )
            with col2:
                docx_data = self.generate_word_doc(st.session_state.response)
                st.download_button(
                    label="Download as Word Document",
                    data=docx_data,
                    file_name="response.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    def extract_images_from_zip(self, uploaded_file):
        """Extracts images from a ZIP file and stores them as JPEG in zip_images session state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract files to a temporary directory
            with ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Convert and add JPEG images to zip_images session state
            st.session_state.zip_images.clear()  # Clear any previous images from zip_images
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(root, file)
                        image = Image.open(image_path)
                        st.session_state.zip_images.append(self.convert_to_jpeg(image))

    def check_for_pasted_image(self):
        """Check for an image in the clipboard and add it to clipboard_images if found."""
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                jpeg_image = self.convert_to_jpeg(image)
                if jpeg_image not in st.session_state.clipboard_images:  # Avoid duplicates
                    st.session_state.clipboard_images.append(jpeg_image)
                st.experimental_rerun()  # Rerun to update image display
        except Exception:
            pass  # Suppress clipboard errors quietly

    def convert_to_jpeg(self, image):
        """Convert an image to JPEG format and return it as a PIL Image."""
        output = BytesIO()
        image.convert("RGB").save(output, format="JPEG")
        output.seek(0)
        return Image.open(output)

    def format_response(self, text):
        # Custom styling with background color, padding, and scrollable div
        formatted_text = ""
        lines = text.splitlines()
        for line in lines:
            if line.startswith("1. ") or line.startswith("2. "):
                formatted_text += f"<li>{line[3:]}</li>"
            elif "**" in line:
                formatted_text += f"<p><b>{line}</b></p>"
            else:
                formatted_text += f"<p>{line}</p>"

        return f"""
            <div style="background-color: #f0f4f8; padding: 20px; border-radius: 8px; border: 1px solid #ddd;
                        font-family: Arial, sans-serif; color: #333; max-height: 300px; overflow-y: scroll;">
                {formatted_text}
            </div>
        """

    def generate_pdf(self, text):
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.setFont("Helvetica", 12)

        width, height = letter
        text_lines = text.splitlines()
        y_position = height - 40
        for line in text_lines:
            if y_position <= 40:
                pdf.showPage()
                y_position = height - 40
            pdf.drawString(40, y_position, line)
            y_position -= 14

        pdf.save()
        pdf_buffer.seek(0)
        return pdf_buffer

    def generate_word_doc(self, text):
        doc_buffer = BytesIO()
        doc = Document()
        doc.add_paragraph(text)
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer
