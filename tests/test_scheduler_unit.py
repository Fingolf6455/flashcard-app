"""
Unit tests for scheduler.py - Spaced repetition algorithm testing
Tests the business logic of spaced repetition without database dependencies
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from scheduler import SpacedRepetitionScheduler, is_card_due_for_review


class TestSpacedRepetitionScheduler:
    """Unit tests for SpacedRepetitionScheduler class"""
    
    def test_schedule_next_review_easy_card(self):
        """Test that easy cards are scheduled for 3 days later"""
        mock_card = Mock()
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_now = datetime(2023, 8, 15, 10, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            next_review = SpacedRepetitionScheduler.schedule_next_review(mock_card, 'easy')
            
            expected = mock_now + timedelta(days=3)
            assert next_review == expected
    
    def test_schedule_next_review_hard_card(self):
        """Test that hard cards are scheduled for 1 day later"""
        mock_card = Mock()
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_now = datetime(2023, 8, 15, 10, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            next_review = SpacedRepetitionScheduler.schedule_next_review(mock_card, 'hard')
            
            expected = mock_now + timedelta(days=1)
            assert next_review == expected
    
    def test_update_card_review_easy(self):
        """Test updating card review tracking for easy card"""
        mock_card = Mock()
        mock_card.review_count = 2
        mock_card.ease_factor = 2.5
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_now = datetime(2023, 8, 15, 10, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            with patch('scheduler.db.session.commit'):
                result = SpacedRepetitionScheduler.update_card_review(mock_card, 'easy')
                
                # Verify card was updated
                assert mock_card.last_reviewed == mock_now
                assert mock_card.review_count == 3
                assert mock_card.ease_factor == 2.6  # Increased by 0.1
                assert mock_card.next_review == mock_now + timedelta(days=3)
                assert result == mock_card
    
    def test_update_card_review_hard(self):
        """Test updating card review tracking for hard card"""
        mock_card = Mock()
        mock_card.review_count = 1
        mock_card.ease_factor = 2.5
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_now = datetime(2023, 8, 15, 10, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            with patch('scheduler.db.session.commit'):
                result = SpacedRepetitionScheduler.update_card_review(mock_card, 'hard')
                
                # Verify card was updated
                assert mock_card.last_reviewed == mock_now
                assert mock_card.review_count == 2
                assert mock_card.ease_factor == 2.3  # Decreased by 0.2
                assert mock_card.next_review == mock_now + timedelta(days=1)
                assert result == mock_card
    
    def test_ease_factor_bounds(self):
        """Test that ease factor stays within bounds"""
        # Test upper bound
        mock_card_high = Mock()
        mock_card_high.review_count = 0
        mock_card_high.ease_factor = 2.9
        
        with patch('scheduler.datetime'), patch('scheduler.db.session.commit'):
            SpacedRepetitionScheduler.update_card_review(mock_card_high, 'easy')
            assert mock_card_high.ease_factor == 3.0  # Capped at 3.0
        
        # Test lower bound
        mock_card_low = Mock()
        mock_card_low.review_count = 0
        mock_card_low.ease_factor = 1.4
        
        with patch('scheduler.datetime'), patch('scheduler.db.session.commit'):
            SpacedRepetitionScheduler.update_card_review(mock_card_low, 'hard')
            assert mock_card_low.ease_factor == 1.3  # Floor at 1.3


class TestCardDueForReview:
    """Unit tests for individual card review checking"""
    
    def test_is_card_due_never_reviewed(self):
        """Test that cards never reviewed are always due"""
        mock_card = Mock()
        mock_card.next_review = None
        
        assert is_card_due_for_review(mock_card) is True
    
    def test_is_card_due_overdue(self):
        """Test that overdue cards are due for review"""
        mock_card = Mock()
        mock_card.next_review = datetime(2023, 8, 10, 10, 0, 0)  # Past date
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 8, 15, 10, 0, 0)
            
            assert is_card_due_for_review(mock_card) is True
    
    def test_is_card_due_future(self):
        """Test that cards scheduled for future are not due"""
        mock_card = Mock()
        mock_card.next_review = datetime(2023, 8, 20, 10, 0, 0)  # Future date
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 8, 15, 10, 0, 0)
            
            assert is_card_due_for_review(mock_card) is False
    
    def test_is_card_due_exact_time(self):
        """Test that cards due exactly now are considered due"""
        mock_card = Mock()
        now = datetime(2023, 8, 15, 10, 0, 0)
        mock_card.next_review = now
        
        with patch('scheduler.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = now
            
            assert is_card_due_for_review(mock_card) is True


class TestSchedulerConstants:
    """Unit tests for scheduler configuration"""
    
    def test_interval_constants(self):
        """Test that spaced repetition intervals are reasonable"""
        assert SpacedRepetitionScheduler.WRONG_ANSWER_INTERVAL == 1
        assert SpacedRepetitionScheduler.RIGHT_ANSWER_INTERVAL == 3
        
        # Ensure intervals are positive
        assert SpacedRepetitionScheduler.WRONG_ANSWER_INTERVAL > 0
        assert SpacedRepetitionScheduler.RIGHT_ANSWER_INTERVAL > 0
        
        # Ensure right answer interval is longer than wrong answer
        assert (SpacedRepetitionScheduler.RIGHT_ANSWER_INTERVAL > 
                SpacedRepetitionScheduler.WRONG_ANSWER_INTERVAL)


class TestEdgeCases:
    """Unit tests for edge cases in spaced repetition logic"""
    
    def test_multiple_easy_reviews(self):
        """Test that multiple easy reviews continue to increase ease factor"""
        mock_card = Mock()
        mock_card.review_count = 0
        mock_card.ease_factor = 2.5
        
        with patch('scheduler.datetime'), patch('scheduler.db.session.commit'):
            # First easy review
            SpacedRepetitionScheduler.update_card_review(mock_card, 'easy')
            assert mock_card.ease_factor == 2.6
            
            # Second easy review
            SpacedRepetitionScheduler.update_card_review(mock_card, 'easy')
            assert mock_card.ease_factor == 2.7
    
    def test_multiple_hard_reviews(self):
        """Test that multiple hard reviews continue to decrease ease factor"""
        mock_card = Mock()
        mock_card.review_count = 0
        mock_card.ease_factor = 2.5
        
        with patch('scheduler.datetime'), patch('scheduler.db.session.commit'):
            # First hard review
            SpacedRepetitionScheduler.update_card_review(mock_card, 'hard')
            assert mock_card.ease_factor == 2.3
            
            # Second hard review  
            SpacedRepetitionScheduler.update_card_review(mock_card, 'hard')
            assert abs(mock_card.ease_factor - 2.1) < 0.001  # Handle float precision
    
    def test_review_count_increments(self):
        """Test that review count always increments regardless of difficulty"""
        mock_card = Mock()
        mock_card.review_count = 5
        mock_card.ease_factor = 2.5
        
        with patch('scheduler.datetime'), patch('scheduler.db.session.commit'):
            SpacedRepetitionScheduler.update_card_review(mock_card, 'easy')
            assert mock_card.review_count == 6
            
            SpacedRepetitionScheduler.update_card_review(mock_card, 'hard')
            assert mock_card.review_count == 7
