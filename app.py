from flask import Flask, request, jsonify, render_template
from llm_client import LlmClient
from utils import is_valid
from models import db, Card
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Initialize LLM client
llm_client = LlmClient()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """generate flashcards from the notes/user input"""
    
    # Get the raw text from request
    data = request.get_json()
    if not data or 'notes' not in data:
        return "Error: Please provide 'notes' in JSON", 400
    
    notes = data['notes']
    
    try:
        # Generate flashcards from notes (prompt formatting handled in LLM client)
        flashcards = llm_client.generate_flashcards(notes)
        
        # Simple validation check
        if not is_valid(flashcards):
            return jsonify({"error": "Invalid flashcards generated"}), 500
        
        # Save cards to database and return with IDs
        saved_cards = []
        for card_data in flashcards:
            # Create new card instance from LLM-generated data
            card = Card(
                question=card_data['question'],
                answer=card_data['answer'],
                hint=card_data.get('hint'),  # Optional field
                # Store tags as JSON string for database compatibility
                tags=json.dumps(card_data.get('tags', [])) if card_data.get('tags') else None
            )
            
            # Save to database (each card gets a unique ID)
            db.session.add(card)
            db.session.commit()
            
            # Add to response with database ID for frontend display
            saved_cards.append(card.to_dict())
        
        return jsonify(saved_cards)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/cards', methods=['GET'])
def get_all_cards():
    """Get all saved cards from database, ordered by creation date (newest first)
    
    Returns:
        JSON array of all flashcard objects with their database IDs
        Used by frontend to display saved cards collection
    """
    try:
        # Fetch all cards ordered by creation date (newest first)
        cards = Card.query.order_by(Card.created_at.desc()).all()
        # Convert to dictionaries for JSON serialization
        return jsonify([card.to_dict() for card in cards])
    except Exception as e:
        return jsonify({"error": f"Error retrieving cards: {str(e)}"}), 500

@app.route('/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get a specific card by its database ID
    
    Args:
        card_id (int): Database ID of the flashcard to retrieve
        
    Returns:
        JSON object of the specific flashcard, or 404 if not found
        Used for individual card access and future study mode features
    """
    try:
        # Look up card by primary key
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({"error": "Card not found"}), 404
        return jsonify(card.to_dict())
    except Exception as e:
        return jsonify({"error": f"Error retrieving card: {str(e)}"}), 500

@app.route('/study', methods=['GET'])
def get_random_card():
    """Get a random card for study session
    
    Returns:
        JSON object of a random flashcard for studying
        Returns 404 if no cards exist in database
    """
    try:
        # Get total count of cards
        total_cards = Card.query.count()
        if total_cards == 0:
            return jsonify({"error": "No cards available for study"}), 404
        
        # Get a random card using SQL RANDOM() function
        random_card = Card.query.order_by(db.func.random()).first()
        return jsonify(random_card.to_dict())
    except Exception as e:
        return jsonify({"error": f"Error getting study card: {str(e)}"}), 500

@app.route('/study/<int:card_id>', methods=['POST'])
def mark_card_studied(card_id):
    """Mark a card as studied (simple tracking for now)
    
    Args:
        card_id (int): Database ID of the card that was studied
        
    Returns:
        JSON confirmation that card was marked as studied
        This is a placeholder for future spaced repetition features
    """
    try:
        # Verify card exists
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({"error": "Card not found"}), 404
        
        # For now, just return success (future: update last_reviewed, etc.)
        from datetime import datetime
        return jsonify({
            "message": f"Card {card_id} marked as studied",
            "card_id": card_id,
            "studied_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Error marking card as studied: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
