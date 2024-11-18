# Join the Siege - Document Classification System

## Overview
This repository provides a document classification system that leverages OpenAI's GPT-4 for classifying various types of documents like invoices, bank statements, and driver's licenses. The application uses `pdf2image` for PDF to image conversion, which requires Poppler, and is exposed as a Flask API for convenient access and classification.

## Directory Structure
```
join-the-siege/
├── src/
│   ├── app.py                   # Flask application
│   ├── file_processor.py        # Handles file processing
│   ├── image_encoder.py         # Handles image encoding
│   ├── image_classifier.py      # Handles image classification
│   └── utils/
│       └── batch_monitor.py     # Utility for monitoring batch jobs
├── data/
│   └── images/                  # Stores processed images
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Prerequisites

This project requires [Poppler](https://poppler.freedesktop.org/) to be installed on your system in order to use `pdf2image` for converting PDF documents to images.

### Installing Poppler
- **macOS**: Install Poppler using Homebrew:
  ```bash
  brew install poppler
  ```
- **Linux**: Install Poppler using `apt`:
  ```bash
  sudo apt-get install poppler-utils
  ```
- **Windows**: Download the latest Poppler binaries from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/). Extract it and add the path to the `bin` directory to your system's PATH.

After installing Poppler, you can proceed to set up the Python environment.

## Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/join-the-siege.git
   cd join-the-siege
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Flask Application

To run the Flask API, execute the following command:
```bash
python -m src.app
```
The application will be accessible at `http://127.0.0.1:5000`.

### Testing the API
You can test the document classification using `curl`:
```bash
curl -X POST -F 'file=@path_to_pdf.pdf' http://127.0.0.1:5000/classify_file
```
Replace `path_to_pdf.pdf` with the path to your PDF file.

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

