import streamlit as st
from PIL import Image
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
        # Session state for response persistence
        if "response" not in st.session_state:
            st.session_state.response = ""

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
                            jpeg_image_path = os.path.join(temp_dir, f"{os.path.splitext(file)[0]}.jpg")
                            rgb_image = image.convert("RGB")
                            rgb_image.save(jpeg_image_path, format="JPEG")
                            jpeg_images.append(jpeg_image_path)

                if jpeg_images:
                    selected_image_path = image_select(
                        label="Select an image:",
                        images=jpeg_images,
                        use_container_width=True
                    )

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

        # Display the response in an enhanced format
        if st.session_state.response:
            st.markdown("### Generated Response:")

            # Format the response with custom styling, background color, and scroll
            formatted_response = self.format_response(st.session_state.response)
            st.markdown(formatted_response, unsafe_allow_html=True)

            # Copy to Clipboard Button
            if st.button("Copy to Clipboard"):
                st.write(
                    "<script>navigator.clipboard.writeText(`" + st.session_state.response + "`);</script>",
                    unsafe_allow_html=True
                )
                st.success("Response copied to clipboard!")

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
            <div style="
                background-color: #f0f4f8;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #ddd;
                font-family: Arial, sans-serif;
                color: #333;
                max-height: 300px;
                overflow-y: scroll;
            ">
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
