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
            # Create new card instance
            card = Card(
                question=card_data['question'],
                answer=card_data['answer'],
                hint=card_data.get('hint'),
                tags=json.dumps(card_data.get('tags', [])) if card_data.get('tags') else None
            )
            
            # Save to database
            db.session.add(card)
            db.session.commit()
            
            # Add to response with ID
            saved_cards.append(card.to_dict())
        
        return jsonify(saved_cards)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
