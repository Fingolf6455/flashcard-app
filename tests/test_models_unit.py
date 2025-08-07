"""
Unit tests for models.py - Testing Card model methods in isolation
These tests focus on the Card model's methods without database dependencies
"""
import pytest
import json
from datetime import datetime
from models import Card


class TestCardModel:
    """Unit tests for Card model methods"""

    def test_card_creation(self):
        """Test Card object creation with all fields"""
        card = Card(
            question="What is Python?",
            answer="A programming language",
            hint="Think about snakes",
            tags=json.dumps(["programming", "python"]),
        )

        assert card.question == "What is Python?"
        assert card.answer == "A programming language"
        assert card.hint == "Think about snakes"
        assert card.tags == '["programming", "python"]'

    def test_card_creation_minimal(self):
        """Test Card object creation with only required fields"""
        card = Card(question="What is 2+2?", answer="4")

        assert card.question == "What is 2+2?"
        assert card.answer == "4"
        assert card.hint is None
        assert card.tags is None

    def test_card_repr(self):
        """Test Card string representation"""
        card = Card(
            question="This is a very long question that should be truncated in repr",
            answer="Short answer",
        )

        repr_str = repr(card)
        assert "This is a very long question that should be trunca" in repr_str
        assert repr_str.startswith("<Card")
        assert "..." in repr_str


class TestCardToDictMethod:
    """Unit tests for Card.to_dict() method - core serialization logic"""

    def test_to_dict_with_all_fields(self):
        """Test to_dict() with all fields populated"""
        # Create card with mock datetime
        card = Card(
            question="What is Flask?",
            answer="A Python web framework",
            hint="Think about web development",
            tags=json.dumps(["python", "web", "framework"]),
        )
        # Mock the created_at field
        card.id = 42
        card.created_at = datetime(2023, 8, 15, 10, 30, 45)

        result = card.to_dict()

        expected = {
            "id": 42,
            "question": "What is Flask?",
            "answer": "A Python web framework",
            "hint": "Think about web development",
            "tags": ["python", "web", "framework"],
            "created_at": "2023-08-15T10:30:45",
        }

        assert result == expected

    def test_to_dict_with_minimal_fields(self):
        """Test to_dict() with only required fields"""
        card = Card(question="What is 2+2?", answer="4")
        card.id = 1
        card.created_at = datetime(2023, 8, 15, 12, 0, 0)

        result = card.to_dict()

        expected = {
            "id": 1,
            "question": "What is 2+2?",
            "answer": "4",
            "hint": None,
            "tags": [],
            "created_at": "2023-08-15T12:00:00",
        }

        assert result == expected

    def test_to_dict_with_no_created_at(self):
        """Test to_dict() when created_at is None"""
        card = Card(question="Test question", answer="Test answer")
        card.id = 1
        card.created_at = None

        result = card.to_dict()

        assert result["created_at"] is None

    def test_to_dict_tags_parsing_json_array(self):
        """Test that JSON array tags are properly parsed to list"""
        card = Card(question="Test", answer="Test", tags='["tag1", "tag2", "tag3"]')
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["tags"] == ["tag1", "tag2", "tag3"]

    def test_to_dict_tags_parsing_single_string(self):
        """Test that single string tags are converted to list"""
        card = Card(question="Test", answer="Test", tags="single_tag")
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["tags"] == ["single_tag"]

    def test_to_dict_tags_parsing_invalid_json(self):
        """Test that invalid JSON tags fallback to single item list"""
        card = Card(question="Test", answer="Test", tags="invalid json {")
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["tags"] == ["invalid json {"]

    def test_to_dict_tags_empty_string(self):
        """Test that empty string tags result in empty list"""
        card = Card(question="Test", answer="Test", tags="")
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        # Empty string tags should result in empty list (our implementation treats empty as None)
        assert result["tags"] == []

    def test_to_dict_tags_none(self):
        """Test that None tags result in empty list"""
        card = Card(question="Test", answer="Test", tags=None)
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["tags"] == []


class TestCardEdgeCases:
    """Unit tests for edge cases and boundary conditions"""

    def test_unicode_content(self):
        """Test Card with unicode content"""
        card = Card(
            question="What is café in English? ☕",
            answer="Coffee 🇫🇷",
            hint="French word",
            tags=json.dumps(["unicode", "français"]),
        )
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["question"] == "What is café in English? ☕"
        assert result["answer"] == "Coffee 🇫🇷"
        assert result["tags"] == ["unicode", "français"]

    def test_very_long_content(self):
        """Test Card with very long content"""
        long_question = "What is " + "very " * 100 + "long question?"
        long_answer = "This is " + "very " * 100 + "long answer."

        card = Card(question=long_question, answer=long_answer)
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["question"] == long_question
        assert result["answer"] == long_answer

    def test_empty_strings(self):
        """Test Card with empty string content"""
        card = Card(question="", answer="", hint="", tags="")
        card.id = 1
        card.created_at = datetime.now()

        result = card.to_dict()

        assert result["question"] == ""
        assert result["answer"] == ""
        assert result["hint"] == ""
        # Empty string tags should result in empty list
        assert result["tags"] == []
