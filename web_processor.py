import streamlit as st
from web_test_case_generator import WebTestCaseGenerator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from docx import Document

class WebProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or st.session_state.get("api_key")
        if not self.api_key:
            st.error("API key is required for generating responses.")
            return
        self.web_generator = WebTestCaseGenerator(api_key=self.api_key)

    def run(self):
        # Initialize response storage in session state
        if "response" not in st.session_state:
            st.session_state.response = ""

        # Web Data Input
        url = st.text_input("Enter the website URL:")
        if url and st.button("Load Web Data"):
            message = self.web_generator.prepare_web_data(url)
            if st.session_state.get("web_data_loaded"):
                st.success("Web data loaded successfully!")
            else:
                st.error(message)

        # Question input and response generation
        if st.session_state.get("web_data_loaded"):
            question = st.text_area("Enter your question:", height=100)
            if st.button("Generate Web Response") and question:
                response = self.web_generator.generate_response(question)
                st.session_state.response = response or "No response generated. Please check your question and try again."

        # Display the generated response
        if st.session_state.response:
            st.markdown("### Generated Response:")
            formatted_response = self.format_response(st.session_state.response)
            st.markdown(formatted_response, unsafe_allow_html=True)

            # Copy to Clipboard Button
            if st.button("Copy to Clipboard"):
                st.write(
                    f"<script>navigator.clipboard.writeText(`{st.session_state.response}`);</script>",
                    unsafe_allow_html=True
                )
                st.success("Response copied to clipboard!")

            # Download options for PDF and Word document
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
