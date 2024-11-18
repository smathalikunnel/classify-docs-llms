import time
import logging
import json
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchMonitor:
    def __init__(self, api_key):
        """
        Initialize the BatchMonitor with API credentials.

        Args:
            api_key (str): The API key for OpenAI.
        """
        self.client = OpenAI(api_key=api_key)

    def monitor_batch_job(self, batch_job_id):
        """
        Monitor the status of a batch job until completion.

        Args:
            batch_job_id (str): The ID of the batch job to be monitored.

        Returns:
            list: List of classifications from the batch job.
        """
        try:
            # Poll until the batch job is processed
            while True:
                batch_status = self.client.batches.retrieve(batch_job_id)
                if batch_status.status == 'completed':
                    result_file_id = batch_status.output_file_id
                    break
                elif batch_status.status == 'failed':
                    raise ValueError("Batch processing failed.")
                else:
                    logger.info("Batch is still processing. Waiting 5 seconds before checking again...")
                    time.sleep(5)

            # Retrieve the content of the result file
            result = self.client.files.content(result_file_id).content
            result_file_name = "data/batch_job_results.jsonl"
            with open(result_file_name, 'wb') as file:
                file.write(result)
            logger.info(f"Batch Job Results saved to: {result_file_name}")

            # Parse the results file and extract classifications
            classifications = []
            with open(result_file_name, 'r') as file:
                for line in file:
                    result_data = json.loads(line)
                    
                    # Extract custom_id
                    custom_id = result_data.get("custom_id")

                    # Extract category from the content JSON string
                    content = result_data["response"]["body"]["choices"][0]["message"]["content"]
                    category = json.loads(content).get("category")  # Parse the JSON string in "content"

                    # Create the new dictionary
                    result = {
                        "custom_id": custom_id,
                        "category": category
                    }
                    classifications.append(result)

            return classifications
        except Exception as e:
            logger.error(f"Error monitoring batch job: {e}")
            raise
