from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)


openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return '''
    <html>
    <head><title>Flashcard Generator</title></head>
    <body>
        <h1>Flashcard Generator</h1>
        <form id="noteForm">
            <h3>Paste your study notes:</h3>
            <textarea id="notes" rows="10" cols="80" placeholder="Enter your study notes here..."></textarea><br><br>
            <button type="button" onclick="generateFlashcards()">Generate Flashcards</button>
        </form>
        
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
        function generateFlashcards() {
            const notes = document.getElementById('notes').value;
            if (!notes.trim()) {
                alert('Please enter some notes!');
                return;
            }
            
            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({notes: notes})
            })
            .then(response => response.text())
            .then(data => {
                document.getElementById('result').innerHTML = '<h3>Generated Flashcards:</h3><pre>' + data + '</pre>';
            })
            .catch(error => {
                document.getElementById('result').innerHTML = '<h3>Error:</h3><pre>' + error + '</pre>';
            });
        }
        </script>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    """Giant function that does everything - this is the dirty spike"""
    
    # Get the raw text from request
    data = request.get_json()
    if not data or 'notes' not in data:
        return "Error: Please provide 'notes' in JSON", 400
    
    notes = data['notes']
    
    # this function creates a prompt for the AI to generate flashcards from the notes/user input
    prompt = f"""
You are a flashcard generator. Given the following study notes, create flashcards in JSON format.

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
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful flashcard generator."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1000,
            temperature=1
        )
        
        # Extract and return raw response
        raw_content = response.choices[0].message.content.strip()
        
        # Return raw string 
        return raw_content
        
    except Exception as e:
        return f"Error generating flashcards: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
