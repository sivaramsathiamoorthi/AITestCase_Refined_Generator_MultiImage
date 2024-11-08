import os
import streamlit as st
from streamlit_image_select import image_select


class MultiImageSelector:
    def __init__(self):
        self.images = []
        self.captions = []

    def load_images_from_folder(self, folder_path):
        """
        Loads images from the specified folder.

        Args:
            folder_path (str): The path to the folder containing images.

        Returns:
            list: A list of image paths.
        """
        allowed_extensions = ('.jpg', '.jpeg', '.png')

        # Verify if the folder exists
        if not os.path.exists(folder_path):
            st.error("The specified folder does not exist.")
            return []

        # Get all image files in the folder
        self.images = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(allowed_extensions)
        ]
        self.captions = [f"Image {i + 1}" for i in range(len(self.images))]

        return self.images

    def display(self, label="Select an image:", use_container_width=True):
        """
        Displays the image selection widget if images are available.

        Args:
            label (str): Label for the image selection widget.
            use_container_width (bool): Whether to use the full container width for the images.

        Returns:
            str: The selected image, or None if no images are available.
        """
        if not self.images:
            st.warning("The folder does not contain any images.")
            return None
        else:
            # Display the image selection widget and return the selected image
            selected_image = image_select(
                label=label,
                images=self.images,
                captions=self.captions,
                use_container_width=use_container_width
            )
            return selected_image
