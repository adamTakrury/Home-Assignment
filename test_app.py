import pytest
import os
from unittest.mock import patch
from app import app  # Import the Flask app

@pytest.fixture
def client():
    # Set the TESTING environment variable
    os.environ["TESTING"] = "True"

    # Configure the app for testing
    app.config['TESTING'] = True

    # Create a test client
    with app.test_client() as client:
        yield client

    # Clean up the TESTING environment variable
    del os.environ["TESTING"]

def test_ask_endpoint_without_database(client):
    with patch("requests.post") as mock_post:
        mock_response = {
            "choices": [
                {"message": {"content": "This is a mocked response from the AI."}}
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        # Prepare the JSON payload
        payload = {
            "question": "What is the capital of France?"
        }

        # Send a POST request to the /ask endpoint
        response = client.post('/ask', json=payload)

    # Check that the response status code is 200
    assert response.status_code == 200

    # Verify the response data
    response_data = response.get_json()
    assert response_data['question'] == "What is the capital of France?"
    assert response_data['answer'] == "This is a mocked response from the AI."

def test_ask_endpoint_with_empty_question(client):
    # Send a POST request with an empty question
    payload = {
        "question": ""
    }

    # Send the request
    response = client.post('/ask', json=payload)

    # Check that the response status code is 400 (Bad Request)
    assert response.status_code == 400

    # Verify the error message in the response
    response_data = response.get_json()
    assert response_data['error'] == "No question provided"

def test_ask_endpoint_with_no_question_key(client):
    # Send a POST request with a missing 'question' key
    payload = {}

    # Send the request
    response = client.post('/ask', json=payload)

    # Check that the response status code is 400 (Bad Request)
    assert response.status_code == 400

    # Verify the error message in the response
    response_data = response.get_json()
    assert response_data['error'] == "No question provided"

def test_ask_endpoint_with_non_json_data(client):
    # Send a POST request with data that is not JSON
    response = client.post('/ask', data="This is not JSON")

    # Check that the response status code is 400 (Bad Request)
    assert response.status_code == 400

    # Verify the error message in the response
    response_data = response.get_json()
    assert response_data['error'] == "Invalid request format, JSON expected"

def test_ask_endpoint_with_large_question(client):
    # Mock the OpenAI API response
    with patch("requests.post") as mock_post:
        mock_response = {
            "choices": [
                {"message": {"content": "This is a mocked response for a large question."}}
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        # Prepare a large question payload
        large_question = "What is the capital of France?" * 1000
        payload = {
            "question": large_question
        }

        # Send a POST request to the /ask endpoint
        response = client.post('/ask', json=payload)

    # Check that the response status code is 200
    assert response.status_code == 200

    # Verify the response data
    response_data = response.get_json()
    assert response_data['question'] == large_question
    assert response_data['answer'] == "This is a mocked response for a large question."

def test_ask_endpoint_with_external_api_failure(client):
    # Mock the OpenAI API response to simulate a failure
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {"error": "Internal Server Error"}

        # Prepare the JSON payload
        payload = {
            "question": "What is the capital of France?"
        }

        # Send a POST request to the /ask endpoint
        response = client.post('/ask', json=payload)

    # Check that the response status code matches the external service failure
    assert response.status_code == 500

    # Verify the error message in the response
    response_data = response.get_json()
    assert "error" in response_data
