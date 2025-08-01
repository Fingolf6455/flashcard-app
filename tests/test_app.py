import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_flashcards_returns_json(client):
    """Test that /generate endpoint returns JSON - this will fail initially"""
    
    # Test data
    test_notes = "Photosynthesis is the process by which plants convert light energy into chemical energy."
    
    # Make POST request to /generate
    response = client.post('/generate', 
                          json={'notes': test_notes},
                          content_type='application/json')
    
    # Expect 200 status
    assert response.status_code == 200
    
    # This test expects JSON but the current app returns a raw string
    # This should FAIL because the app returns raw text, not JSON
    try:
        json_data = response.get_json()
        assert json_data is not None, "Response should be valid JSON"
        assert isinstance(json_data, list), "Response should be a list of flashcards"
    except Exception as e:
        # This will fail because the app returns raw string instead of JSON
        pytest.fail(f"Expected JSON response but got: {response.get_data(as_text=True)}")