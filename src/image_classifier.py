import logging
from dotenv import load_dotenv
import json
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageClassifier:
    def __init__(self, api_key, categories, fine_tuned_models=None):
        """
        Initialize the ImageClassifier with API credentials and categories.

        Args:
            api_key (str): The API key for OpenAI.
            categories (list): List of categories for classification.
            fine_tuned_models (dict, optional): Dictionary of fine-tuned models.
        """
        self.client = OpenAI(api_key=api_key)
        self.categories = categories
        self.fine_tuned_models = fine_tuned_models or {}
        self.classification_system_prompt = (
            f"Your goal is to classify the images into one of the following categories: {', '.join(self.categories)}."
        )
        self.resp_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "Classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {"title": "Category", "type": "string"}
                    },
                    "required": ["category"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }

    def classify_image(self, base64_image):
        """
        Classify a single image.

        Args:
            base64_image (str): Base64 encoded string of the image.

        Returns:
            dict: Classification result.
        """
        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": self.classification_system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.2,
                response_format=self.resp_format
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error classifying image: {e}")
            raise

    def create_batch_request(self, images_dict):
        """
        Create a batch request for multiple images.

        Args:
            images_dict (dict): Dict of image paths and base64 encoded images.

        Returns:
            list: List of tasks for batch processing.
        """
        tasks = []
        for i, (img_path,base64_image) in enumerate(images_dict.items()):
            task = {
                "custom_id": f"task-{img_path}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-2024-08-06",
                    "temperature": 0.2,
                    "response_format": self.resp_format,
                    "messages": [
                        {"role": "system", "content": self.classification_system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ]
                }
            }
            tasks.append(task)

        return tasks

    def execute_batch_job(self, tasks):
        """
        Execute the batch job for the given tasks.

        Args:
            tasks (list): List of tasks to be executed.

        Returns:
            str: ID of the created batch job.
        """
        try:
            batch_file_name = "data/batch_tasks.jsonl"
            with open(batch_file_name, 'w') as file:
                for task in tasks:
                    file.write(json.dumps(task) + '\n')

            batch_file = self.client.files.create(file=open(batch_file_name, "rb"), purpose="batch")
            batch_job = self.client.batches.create(
                input_file_id=batch_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )

            logger.info(f"Batch Job Created: {batch_job.id}")
            return batch_job.id
        except Exception as e:
            logger.error(f"Error executing batch job: {e}")
            raise
