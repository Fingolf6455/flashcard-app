from flask import Flask, request, jsonify, render_template
from llm_client import LlmClient
from utils import is_valid
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Extract prompt as constant
PROMPT_TEMPLATE = """You are a flashcard generator. Given the following study notes, create flashcards in JSON format.

Each flashcard should have:
- question: A clear question based on the content
- answer: The correct answer
- hint: A helpful hint (optional)
- tags: Relevant tags as an array

Notes to process:
{notes}

Return only valid JSON array of flashcard objects. Example:
[
  {{
    "question": "What is photosynthesis?",
    "answer": "The process by which plants convert light energy into chemical energy",
    "hint": "Think about how plants make food",
    "tags": ["biology", "plants"]
  }}
]
"""

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
    
    # Use extracted prompt template
    prompt = PROMPT_TEMPLATE.format(notes=notes)
    
    try:
        # Use extracted LLM client
        flashcards = llm_client.generate_flashcards(prompt)
        
        # Simple validation check
        if not is_valid(flashcards):
            return jsonify({"error": "Invalid flashcards generated"}), 500
        
        return jsonify(flashcards)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
