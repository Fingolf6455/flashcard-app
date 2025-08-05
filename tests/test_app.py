import pytest
import json
from app import app, db

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_flashcards_returns_json(client):
    """Integration test that /generate endpoint returns valid JSON from real LLM"""
    
    # Test data 
    test_notes = "Water freezes at 0 degrees Celsius and boils at 100 degrees Celsius."
    
    # Make POST request to /generate
    response = client.post('/generate', 
                          json={'notes': test_notes},
                          content_type='application/json')
    
    # Expect 200 status
    assert response.status_code == 200
    
    # Verify JSON response structure
    json_data = response.get_json()
    assert json_data is not None, "Response should be valid JSON"
    assert isinstance(json_data, list), "Response should be a list of flashcards"
    assert len(json_data) > 0, "Should return at least one flashcard"
    
    # Verify flashcard structure
    flashcard = json_data[0]
    assert "question" in flashcard, "Flashcard should have a question"
    assert "answer" in flashcard, "Flashcard should have an answer"
    assert "id" in flashcard, "Flashcard should have a database ID"
    assert isinstance(flashcard.get("tags", []), list), "Tags should be a list"
    assert isinstance(flashcard["id"], int), "ID should be an integer"
    
    # Basic content validation
    assert len(flashcard["question"]) > 0, "Question should not be empty"
    assert len(flashcard["answer"]) > 0, "Answer should not be empty"
    assert flashcard["id"] > 0, "ID should be positive"