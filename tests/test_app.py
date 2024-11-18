from io import BytesIO
import pytest
from src.app import app
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_no_file_in_request(client):
    response = client.post('/classify_file')
    assert response.status_code == 400

def test_no_selected_file(client):
    data = {'file': (BytesIO(b""), '')}  # Empty filename
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

def test_success(client, mocker):
    # Mock the FileProcessor's process_file to avoid actual file processing
    mocker.patch('src.file_processor.FileProcessor.process_file', return_value="dummy_image_path")
    # Mock the ImageEncoder's encode_image method to return a dummy base64 encoded string
    mocker.patch('src.image_encoder.ImageEncoder.encode_image', return_value="dummy_base64_string")
    # Mock the ImageClassifier's classify_image method
    mocker.patch('src.app.ImageClassifier.classify_image', return_value={"category": "test_class"})

    data = {'file': (BytesIO(b"dummy content"), 'file.pdf')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json() == {"classification": {"category": "test_class"}}


def test_classify_files(client, mocker):
    mock_response = {
        "classifications": [
            {"category": "driver's license", "custom_id": "task-files/drivers_license_1.jpg"},
            {"category": "driver's license", "custom_id": "task-files/drivers_license_3.jpg"},
            {"category": "bank statement", "custom_id": "task-data/images/bank_statement_1_page_1.png"},
            {"category": "driver's license", "custom_id": "task-files/drivers_licence_2.jpg"},
            {"category": "bank statement", "custom_id": "task-data/images/bank_statement_3_page_1.png"},
            {"category": "bank statement", "custom_id": "task-data/images/bank_statement_2_page_1.png"},
            {"category": "invoice", "custom_id": "task-data/images/invoice_1_page_1.png"},
            {"category": "invoice", "custom_id": "task-data/images/invoice_2_page_1.png"},
            {"category": "invoice", "custom_id": "task-data/images/invoice_3_page_1.png"}
        ]
    }

    mocker.patch('src.app.BatchMonitor.monitor_batch_job', return_value=mock_response["classifications"])

    response = client.get('/classify_files')
    assert response.status_code == 200
    assert response.get_json() == mock_response

# Renamed test for clarity and avoid pytest confusion
@pytest.mark.parametrize("filename, expected", [
    ("file.pdf", True),
    ("file.png", True),
    ("file.jpg", True),
    ("file.txt", False),
    ("file", False),
])
def test_allowed_file_extension(filename, expected):
    allowed_extensions = {"pdf", "png", "jpg", "jpeg"}
    result = filename.split('.')[-1].lower() in allowed_extensions if '.' in filename else False
    assert result == expected
