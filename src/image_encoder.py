import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageEncoder:
    @staticmethod
    def encode_image(image_path):
        """
        Encode an image to base64 format.

        Args:
            image_path (str): The path to the image file to be encoded.

        Returns:
            str: Base64 encoded string of the image.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            raise
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise