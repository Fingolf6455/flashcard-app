import pytest
import json
import tempfile
import os
from app import app, db, Card


@pytest.fixture
def test_app():
    """Create a test Flask app with an in-memory database"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_app):
    """Create a test client"""
    return test_app.test_client()


@pytest.fixture
def app_context(test_app):
    """Provide application context for database operations"""
    with test_app.app_context():
        yield


class TestCardModel:
    """Tests for the Card model"""

    def test_card_creation(self, app_context):
        """Test creating a card and saving to database"""
        # Clear any existing data in the test database
        Card.query.delete()
        db.session.commit()

        card = Card(
            question="What is Python?",
            answer="A programming language",
            hint="Think about snakes",
            tags=json.dumps(["programming", "python"]),
        )

        db.session.add(card)
        db.session.commit()

        # Verify card was saved
        saved_card = Card.query.first()
        assert saved_card is not None
        assert saved_card.question == "What is Python?"
        assert saved_card.answer == "A programming language"
        assert saved_card.hint == "Think about snakes"
        assert saved_card.created_at is not None

    def test_card_to_dict(self, app_context):
        """Test Card.to_dict() method"""
        card = Card(
            question="Test question",
            answer="Test answer",
            hint="Test hint",
            tags=json.dumps(["tag1", "tag2"]),
        )

        db.session.add(card)
        db.session.commit()

        card_dict = card.to_dict()

        assert card_dict["id"] == card.id
        assert card_dict["question"] == "Test question"
        assert card_dict["answer"] == "Test answer"
        assert card_dict["hint"] == "Test hint"
        assert card_dict["tags"] == ["tag1", "tag2"]
        assert "created_at" in card_dict

    def test_card_tags_handling(self, app_context):
        """Test different tag formats are handled correctly"""
        # Test with JSON array
        card1 = Card(question="Q1", answer="A1", tags=json.dumps(["tag1", "tag2"]))
        db.session.add(card1)

        # Test with None tags
        card2 = Card(question="Q2", answer="A2", tags=None)
        db.session.add(card2)

        # Test with single string (fallback case)
        card3 = Card(question="Q3", answer="A3", tags="single_tag")
        db.session.add(card3)

        db.session.commit()

        # Verify tag parsing
        assert card1.to_dict()["tags"] == ["tag1", "tag2"]
        assert card2.to_dict()["tags"] == []
        assert card3.to_dict()["tags"] == ["single_tag"]


class TestDatabaseIntegration:
    """Tests for database integration with endpoints"""

    def test_generate_saves_to_database(self, client, app_context):
        """Test that /generate endpoint saves cards to database"""
        # Get initial count
        initial_count = Card.query.count()

        # Generate flashcards
        response = client.post(
            "/generate",
            json={
                "notes": "The sun is a star. Stars produce light through nuclear fusion."
            },
            content_type="application/json",
        )

        assert response.status_code == 200

        # Check that cards were saved to database
        final_count = Card.query.count()
        assert final_count > initial_count

        # Verify response contains IDs
        json_data = response.get_json()
        for card in json_data:
            assert "id" in card
            assert isinstance(card["id"], int)
            assert card["id"] > 0

    def test_generate_returns_saved_cards_with_ids(self, client, app_context):
        """Test that generated cards have database IDs in response"""
        response = client.post(
            "/generate",
            json={"notes": "Photosynthesis converts sunlight into energy."},
            content_type="application/json",
        )

        assert response.status_code == 200
        json_data = response.get_json()

        # Each card should have an ID from the database
        for card_data in json_data:
            assert "id" in card_data
            card_id = card_data["id"]

            # Verify the card exists in database with that ID
            saved_card = db.session.get(Card, card_id)
            assert saved_card is not None
            assert saved_card.question == card_data["question"]
            assert saved_card.answer == card_data["answer"]

    def test_database_persistence(self, client, app_context):
        """Test that cards persist between requests"""
        # Generate some cards
        client.post(
            "/generate",
            json={"notes": "Rome is the capital of Italy."},
            content_type="application/json",
        )

        first_count = Card.query.count()

        # Generate more cards
        client.post(
            "/generate",
            json={"notes": "Paris is the capital of France."},
            content_type="application/json",
        )

        second_count = Card.query.count()

        # Verify cards accumulated
        assert second_count > first_count

        # Verify all cards are still there
        all_cards = Card.query.all()
        assert len(all_cards) == second_count


class TestDatabaseErrorHandling:
    """Tests for database error scenarios"""

    def test_invalid_notes_doesnt_corrupt_database(self, client, app_context):
        """Test that invalid requests don't corrupt database state"""
        initial_count = Card.query.count()

        # Send invalid request
        response = client.post(
            "/generate", json={}, content_type="application/json"  # Missing 'notes'
        )

        # Should return error
        assert response.status_code == 400

        # Database should be unchanged
        final_count = Card.query.count()
        assert final_count == initial_count
