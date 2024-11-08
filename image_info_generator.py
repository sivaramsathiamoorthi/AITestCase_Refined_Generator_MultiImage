# image_info_generator.py
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, AIMessage
import base64
import tempfile
from PIL import Image


class ImageInfoGenerator:
    def __init__(self, model_name="gpt-4o-mini", temperature=0.5, api_key=None):
        # Initialize the ChatOpenAI model with an API key if provided
        self.model = ChatOpenAI(model=model_name, max_tokens=1024, openai_api_key=api_key)

    def encode_image(self, image):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
            image.save(temp_image.name)
            with open(temp_image.name, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

    def generate_image_description(self, image, question):
        base64_image = self.encode_image(image)
        prompt = question if question else "Identify all items in this image and provide a list of what you see."

        try:
            msg = self.model.invoke(
                [
                    AIMessage(content="You are a highly skilled business analyst. Based on your expertise in analyzing data, "
                                      "interpreting business requirements, and understanding complex processes, examine the provided context. "
                                      "Deliver a detailed analysis that outlines key insights, identifies potential risks, and highlights any "
                                      "opportunities for improvement. Provide a structured response, including specific recommendations or steps for "
                                      "optimization where applicable. Present your findings in a clear and actionable format to support data-driven "
                                      "decision-making."),
                    HumanMessage(
                        content=[
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    )
                ]
            )
            return msg.content
        except Exception as e:
            return f"Error generating image description: {e}"
