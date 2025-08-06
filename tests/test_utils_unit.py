"""
Unit tests for utils.py - Testing validation functions in isolation
These are true unit tests that test individual functions without external dependencies
"""
import pytest
from utils import is_valid_card, is_valid


class TestCardValidation:
    """Unit tests for individual card validation"""
    
    def test_is_valid_card_with_valid_card(self):
        """Test that a properly structured card passes validation"""
        valid_card = {
            'question': 'What is Python?',
            'answer': 'A programming language',
            'hint': 'Think about snakes',
            'tags': ['programming']
        }
        
        assert is_valid_card(valid_card) is True
    
    def test_is_valid_card_missing_question(self):
        """Test that card without question fails validation"""
        invalid_card = {
            'answer': 'A programming language',
            'hint': 'Think about snakes'
        }
        
        assert is_valid_card(invalid_card) is False
    
    def test_is_valid_card_missing_answer(self):
        """Test that card without answer fails validation"""
        invalid_card = {
            'question': 'What is Python?',
            'hint': 'Think about snakes'
        }
        
        assert is_valid_card(invalid_card) is False
    
    def test_is_valid_card_empty_question(self):
        """Test that card with empty question fails validation"""
        invalid_card = {
            'question': '',
            'answer': 'A programming language'
        }
        
        assert is_valid_card(invalid_card) is False
    
    def test_is_valid_card_empty_answer(self):
        """Test that card with empty answer fails validation"""
        invalid_card = {
            'question': 'What is Python?',
            'answer': ''
        }
        
        assert is_valid_card(invalid_card) is False
    
    def test_is_valid_card_whitespace_only(self):
        """Test that card with whitespace-only content fails validation"""
        invalid_card = {
            'question': '   ',
            'answer': '   '
        }
        
        assert is_valid_card(invalid_card) is False
    
    def test_is_valid_card_not_dict(self):
        """Test that non-dictionary input fails validation"""
        assert is_valid_card("not a dict") is False
        assert is_valid_card(['question', 'answer']) is False
        assert is_valid_card(None) is False


class TestCardsListValidation:
    """Unit tests for cards list validation"""
    
    def test_is_valid_with_valid_cards(self):
        """Test that list of valid cards passes validation"""
        valid_cards = [
            {'question': 'Q1', 'answer': 'A1'},
            {'question': 'Q2', 'answer': 'A2'}
        ]
        
        assert is_valid(valid_cards) is True
    
    def test_is_valid_with_empty_list(self):
        """Test that empty list fails validation"""
        assert is_valid([]) is False
    
    def test_is_valid_with_none(self):
        """Test that None fails validation"""
        assert is_valid(None) is False
    
    def test_is_valid_with_non_list(self):
        """Test that non-list input fails validation"""
        assert is_valid("not a list") is False
        assert is_valid({'question': 'Q', 'answer': 'A'}) is False
    
    def test_is_valid_with_mixed_valid_invalid(self):
        """Test that list with one invalid card fails validation"""
        mixed_cards = [
            {'question': 'Q1', 'answer': 'A1'},  # valid
            {'question': '', 'answer': 'A2'}     # invalid - empty question
        ]
        
        assert is_valid(mixed_cards) is False
    
    def test_is_valid_single_card(self):
        """Test that single valid card in list passes validation"""
        single_card = [{'question': 'Q1', 'answer': 'A1'}]
        
        assert is_valid(single_card) is True


class TestEdgeCases:
    """Unit tests for edge cases and boundary conditions"""
    
    def test_card_with_optional_fields(self):
        """Test that card with only required fields passes validation"""
        minimal_card = {
            'question': 'What is 2+2?',
            'answer': '4'
        }
        
        assert is_valid_card(minimal_card) is True
    
    def test_card_with_extra_fields(self):
        """Test that card with extra fields still passes validation"""
        card_with_extras = {
            'question': 'What is Python?',
            'answer': 'A programming language',
            'hint': 'Think about snakes',
            'tags': ['programming'],
            'difficulty': 'easy',
            'category': 'tech'
        }
        
        assert is_valid_card(card_with_extras) is True
    
    def test_unicode_content(self):
        """Test that cards with unicode content work correctly"""
        unicode_card = {
            'question': 'What is café in English?',
            'answer': 'Coffee ☕',
            'hint': 'French word 🇫🇷'
        }
        
        assert is_valid_card(unicode_card) is True
