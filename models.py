from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Card(db.Model):
    """Flashcard model with basic schema"""
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Card {self.id}: {self.question[:50]}...>'
    
    def to_dict(self):
        """Convert card to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'hint': self.hint,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
