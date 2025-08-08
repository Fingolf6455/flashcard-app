"""
Spaced repetition scheduler for flashcard review timing
Implements simple spaced repetition logic: wrong = review tomorrow, right = review in 3 days
"""
from datetime import datetime, timedelta
from models import Card, db


class SpacedRepetitionScheduler:
    """Simple spaced repetition scheduler for flashcard reviews"""
    
    # Simple intervals: wrong answer = 1 day, right answer = 3 days
    WRONG_ANSWER_INTERVAL = 1  # days
    RIGHT_ANSWER_INTERVAL = 3  # days
    
    @classmethod
    def schedule_next_review(cls, card, difficulty):
        """
        Schedule the next review for a card based on study performance
        
        Args:
            card (Card): The flashcard to schedule
            difficulty (str): 'easy' (knew it) or 'hard' (didn't know it)
            
        Returns:
            datetime: When the card should be reviewed next
        """
        now = datetime.utcnow()
        
        if difficulty == 'easy':
            # Card was easy - review in 3 days
            next_review = now + timedelta(days=cls.RIGHT_ANSWER_INTERVAL)
        else:
            # Card was hard - review tomorrow
            next_review = now + timedelta(days=cls.WRONG_ANSWER_INTERVAL)
        
        return next_review
    
    @classmethod
    def update_card_review(cls, card, difficulty):
        """
        Update a card's review tracking after study session
        
        Args:
            card (Card): The flashcard that was studied
            difficulty (str): 'easy' or 'hard' based on user feedback
            
        Returns:
            Card: Updated card with new review scheduling
        """
        now = datetime.utcnow()
        
        # Update review tracking
        card.last_reviewed = now
        card.review_count += 1
        card.next_review = cls.schedule_next_review(card, difficulty)
        
        # Simple ease factor adjustment (foundation for future SM-2)
        if difficulty == 'easy':
            card.ease_factor = min(card.ease_factor + 0.1, 3.0)  # Cap at 3.0
        else:
            card.ease_factor = max(card.ease_factor - 0.2, 1.3)  # Floor at 1.3
        
        # Save to database
        db.session.commit()
        
        return card
    
    @classmethod
    def get_cards_due_for_review(cls):
        """
        Get all cards that are due for review
        
        Returns:
            List[Card]: Cards that should be studied now
        """
        now = datetime.utcnow()
        
        # Cards due for review: never reviewed OR next_review <= now
        cards_due = Card.query.filter(
            (Card.next_review.is_(None)) | (Card.next_review <= now)
        ).order_by(Card.last_reviewed.asc().nullsfirst()).all()
        
        return cards_due
    
    @classmethod
    def get_review_statistics(cls):
        """
        Get overall review statistics for progress tracking
        
        Returns:
            dict: Statistics about cards and review progress
        """
        total_cards = Card.query.count()
        reviewed_cards = Card.query.filter(Card.last_reviewed.isnot(None)).count()
        cards_due = len(cls.get_cards_due_for_review())
        
        # Calculate average ease factor for cards that have been reviewed
        avg_ease = db.session.query(db.func.avg(Card.ease_factor)).filter(
            Card.review_count > 0
        ).scalar()
        
        return {
            'total_cards': total_cards,
            'reviewed_cards': reviewed_cards,
            'cards_due_for_review': cards_due,
            'cards_not_due': total_cards - cards_due,
            'average_ease_factor': round(avg_ease, 2) if avg_ease else 2.5,
            'review_completion_rate': round((reviewed_cards / total_cards) * 100, 1) if total_cards > 0 else 0
        }


def is_card_due_for_review(card):
    """
    Check if a single card is due for review
    
    Args:
        card (Card): The flashcard to check
        
    Returns:
        bool: True if card should be studied now
    """
    if card.next_review is None:
        return True  # Never reviewed cards are always due
    
    return datetime.utcnow() >= card.next_review


def get_next_study_card():
    """
    Get the next card that should be studied based on spaced repetition
    Prioritizes cards that are overdue
    
    Returns:
        Card or None: Next card to study, or None if no cards are due
    """
    cards_due = SpacedRepetitionScheduler.get_cards_due_for_review()
    
    if not cards_due:
        return None
    
    # Return the card that's been waiting longest for review
    return cards_due[0]
