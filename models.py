from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Card(db.Model):
    """Flashcard model with spaced repetition tracking"""

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Spaced repetition fields
    last_reviewed = db.Column(db.DateTime, nullable=True)
    next_review = db.Column(db.DateTime, nullable=True)
    review_count = db.Column(db.Integer, default=0)
    ease_factor = db.Column(db.Float, default=2.5)  # For future SM-2 algorithm

    def __repr__(self):
        return f"<Card {self.id}: {self.question[:50]}...>"

    def to_dict(self):
        """Convert card to dictionary for JSON serialization"""
        # Parse tags back to list if stored as JSON string
        tags_list = []
        if self.tags:
            try:
                tags_list = (
                    json.loads(self.tags) if self.tags.startswith("[") else [self.tags]
                )
            except (json.JSONDecodeError, AttributeError):
                tags_list = [self.tags]  # Fallback to single tag

        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "hint": self.hint,
            "tags": tags_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "review_count": self.review_count,
            "ease_factor": self.ease_factor,
        }
