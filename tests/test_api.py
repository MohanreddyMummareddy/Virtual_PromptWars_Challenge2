import pytest
from src.app import create_app
from src.config import TestConfig

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test if frontend is served with secure headers."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Start Your Civic Journey" in response.data
    
    # Test Security Criteria Evaluation
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'

def test_chat_route_requires_json(client):
    response = client.post('/api/chat', data="Should fail because not json")
    assert response.status_code == 400

def test_chat_route_requires_message(client):
    response = client.post('/api/chat', json={"context": "some context"})
    assert response.status_code == 400
    assert b"Message body cannot be empty" in response.data

def test_chat_route_valid_request(client):
    # Relies on the mock implementation of LLMService in TestConfig
    response = client.post('/api/chat', json={"message": "hello test", "context": ""})
    assert response.status_code == 200
    assert b"mock response" in response.data.lower()
