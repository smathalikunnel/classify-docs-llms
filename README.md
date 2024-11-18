# Classify documents with LLMs

## Overview
This project is a Flask-based application that allows users to classify files. It includes capabilities to handle various document formats and uses OpenAI to classify the contents.

## Features
- Accepts multiple file formats (PDF, PNG, JPG, xlxs, docx).
- Converts PDFs to images using `pdf2image` with `poppler` as a backend.
- Classifies the content using an OpenAI-powered model.
- Includes a CI/CD pipeline to automate testing and deployment.

## Prerequisites
- Python 3.13
- `poppler-utils` (required for PDF conversion)
- OpenAI API key for classification tasks

## Local Setup Instructions
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/yourusername/classify-docs-llms.git
   cd classify-docs-llms
   ```

2. **Create and Activate Virtual Environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Install Poppler** (for macOS using Homebrew):
   ```sh
   brew install poppler
   ```

5. **Set Up Environment Variables**:
   - Create a `.env` file in the project root to store your OpenAI API key and other secrets.
   - Example `.env` file:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
## Running the Flask Application

To run the Flask API, execute the following command:
```bash
python -m src.app
```
The application will be accessible at `http://127.0.0.1:5001`.

### Testing the API
You can test the document classification using `curl`:
```bash
curl -X POST -F 'file=@path_to_pdf.pdf' http://127.0.0.1:5001/classify_file
```
Replace `path_to_pdf.pdf` with the path to your PDF file.

## CI/CD Pipeline
This project uses GitHub Actions to manage Continuous Integration and Continuous Deployment (CI/CD).

### GitHub Secrets
To keep sensitive data secure, such as the OpenAI API key, GitHub Secrets are used.
- Go to your GitHub repository > **Settings** > **Secrets and variables** > **Actions**.
- Add the following secrets:
  - `OPENAI_API_KEY`: Your OpenAI API key.
  - `GCP_SERVICE_ACCOUNT_KEY`: Google Cloud service account key for deployment to Google Cloud Run.
  - `GCP_PROJECT_ID`: Your Google Cloud project ID.

### CI/CD Workflow Overview
The CI/CD pipeline is defined in the `.github/workflows/ci_cd_workflow.yml` file:
1. **Checkout the Code**: Pulls the latest version of the code.
2. **Set Up Python Environment**: Uses Python 3.13.
3. **Install Dependencies**: Installs `poppler-utils` for PDF processing and other Python dependencies.
4. **Run Tests**: Executes tests using `pytest`. The `OPENAI_API_KEY` is passed securely from GitHub Secrets.
5. **Deploy for Testing**: Deploys the application using Gunicorn to validate the deployment locally.
6. **Verify Deployment**: Tests the deployed API to ensure it's responding correctly.
7. **Deploy to Google Cloud Run (Optional)**: If all tests pass, the Docker image is built and deployed to Google Cloud Run.
8. **Verify Cloud Deployment (Optional)**: Verifies that the application is running on Google Cloud Run by sending a test request.

## Docker Setup
The Dockerfile is used to create a container image for deployment.
- The Dockerfile installs `poppler-utils` and other Python dependencies.
- Flask is run using Gunicorn, which is more suitable for production environments.

### Build and Run Docker Locally
1. **Build Docker Image**:
   ```sh
   docker build -t flask-app .
   ```

2. **Run Docker Container**:
   ```sh
   docker run -p 5001:5001 flask-app
   ```

## Deployment
### Google Cloud Run
The application is deployed to Google Cloud Run as part of the CI/CD pipeline:
- The GitHub Actions workflow builds a Docker image, pushes it to Google Container Registry, and deploys it to Cloud Run.
- Ensure that the Google Cloud project and service account are set up correctly.

## Testing
- Run unit tests with `pytest`:
  ```sh
  pytest
  ```

## Environment Variables
- The application uses the following environment variables:
  - `OPENAI_API_KEY`: Required for interacting with OpenAI's API.
  - Set these variables in your `.env` file for local development and in GitHub Secrets for the CI/CD pipeline.

## Notes
- **Security**: Sensitive information like API keys should not be hardcoded or included in the repository. Use environment variables or GitHub Secrets.
- **Poppler Installation**: Ensure `poppler` is installed both locally (using Homebrew for macOS) and in any Docker or CI/CD environment to avoid runtime errors with `pdf2image`.

## Documentation: Fine-tuning Process
This project supports fine-tuning the model for improved classification. Here are the steps to perform fine-tuning on GPT-4:

1. **Dataset Preparation**: Create a labeled dataset in JSONL format. Each entry should contain the input prompt and the expected output.
   - Example format:
     ```json
     {"prompt": "Classify this document: {document_content}", "completion": ">>> Medical Record"}
     ```

2. **Upload Dataset**: Use the OpenAI API to upload your dataset for fine-tuning:
   ```python
   training_file = openai.File.create(file=open("training_data.jsonl", "rb"), purpose='fine-tune')
   ```

3. **Fine-Tune the Model**: Use the OpenAI FineTune API to create a fine-tuned model:
   ```python
   fine_tune_response = openai.FineTune.create(training_file=training_file.id, model="gpt-4o-2024-08-06", n_epochs=4, suffix="industry-specific-classifier")
   ```

4. **Update the Code**: Update the code by replacing the model name in the `fine_tuned_models` dictionary with the fine-tuned model's name returned by the API.

## Notes
- We are using `ThreadPoolExecutor` instead of `ProcessPoolExecutor` because the operations are I/O-bound (e.g., file reading, API calls).
- In Google Cloud, this logic could be replaced with Cloud Functions, Pub/Sub, and Cloud Run to achieve better scalability and efficiency.
- OpenAI's batch functionality is leveraged to send up to 50,000 requests in a single call, which improves scalability, reduces cost, and helps avoid rate limits.

## Contributing
Contributions are welcome! If you find any issues or have suggestions, please create a pull request or an issue in the GitHub repository.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more information.

