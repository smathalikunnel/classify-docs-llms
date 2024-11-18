
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from src.file_processor import FileProcessor
from src.image_classifier import ImageClassifier
from src.image_encoder import ImageEncoder
from src.utils.batch_monitor import BatchMonitor

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Flask Endpoint for Single File Classification
@app.route('/classify_file', methods=['POST'])
def classify_file():
    """
    Flask endpoint to classify an uploaded file.

    Returns:
        Response: JSON response containing the classification result.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # Save the uploaded file to a temporary directory
        file_path = os.path.join("data/uploads", file.filename)
        os.makedirs("data/uploads", exist_ok=True)
        file.save(file_path)

        # Process the file to generate an image
        file_processor = FileProcessor()
        image_path = file_processor.process_file(file_path)

        # Encode the image for classification
        image_encoder = ImageEncoder()
        encoded_image = image_encoder.encode_image(image_path)

        # Set up classification categories and models
        categories = ["invoice", "bank statement", "driver's license", "other"]
        fine_tuned_models = {
            "finance": "gpt-4o-finetuned-finance",
            "healthcare": "gpt-4o-finetuned-healthcare",
        }

        # Perform classification
        image_classifier = ImageClassifier(api_key=os.getenv('OPENAI_API_KEY'), categories=categories, fine_tuned_models=fine_tuned_models)
        classification_result = image_classifier.classify_image(encoded_image)

        return jsonify({"classification": classification_result}), 200
    except Exception as e:
        logger.error(f"Error in classify_file endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Flask Endpoint for Batch Classification
@app.route('/classify_files', methods=['GET'])
def classify_files():
    """
    Flask endpoint to classify multiple files from the 'files' directory.

    Returns:
        Response: JSON response containing the classification results.
    """
    try:
        # Directory containing files to classify
        files_directory = "files"
        file_paths = [os.path.join(files_directory, f) for f in os.listdir(files_directory) if os.path.isfile(os.path.join(files_directory, f))]

        # Process each file concurrently to generate images
        file_processor = FileProcessor()
        processed_images = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(file_processor.process_file, file_path): file_path for file_path in file_paths}
            for future in as_completed(futures):
                try:
                    image_path = future.result()
                    processed_images.append(image_path)
                    logger.info(f"Successfully processed file: {futures[future]}")
                except Exception as e:
                    logger.error(f"Error processing file {futures[future]}: {e}")

        # Encode images for classification
        image_encoder = ImageEncoder()
        #encoded_images = [image_encoder.encode_image(image_path) for image_path in processed_images]
        encoded_images_dict = {image_path: image_encoder.encode_image(image_path) for image_path in processed_images}

        # Set up classification categories and models
        categories = ["invoice", "bank statement", "driver's license", "other"]
        fine_tuned_models = {
            "finance": "gpt-4o-finetuned-finance",
            "healthcare": "gpt-4o-finetuned-healthcare",
        }

        # Perform batch classification
        image_classifier = ImageClassifier(api_key=os.getenv('OPENAI_API_KEY'), categories=categories, fine_tuned_models=fine_tuned_models)
        tasks = image_classifier.create_batch_request(encoded_images_dict)
        batch_job_id = image_classifier.execute_batch_job(tasks)

        # Monitor the batch job using BatchMonitor
        batch_monitor = BatchMonitor(api_key=os.getenv('OPENAI_API_KEY'))
        classifications = batch_monitor.monitor_batch_job(batch_job_id)

        return jsonify({"classifications": classifications}), 200
    except Exception as e:
        logger.error(f"Error in classify_files endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# # Flask Endpoint for testing Batch Classification
# @app.route('/test_batch', methods=['GET'])
# def monitor_jobs():
# # Assuming there's a batch query endpoint
#     openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     response = openai_client.batches.list()  # Replace 'Batch.list()' with the correct method
#     # Monitor the batch job using BatchMonitor
#     batch_monitor = BatchMonitor(api_key=os.getenv('OPENAI_API_KEY'))
    
#     for batch in response:
#         print(f"Batch {batch}")
#         classifications = batch_monitor.monitor_batch_job(batch.id) #batch_673a72a5bd04819091cf899764b681e2
        
#         return jsonify({"classifications": classifications}), 200
        

if __name__ == "__main__":
    # Run the Flask application
    app.run(host='0.0.0.0', port=5001, debug=True)
