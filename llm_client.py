import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flashcard generation prompt template
FLASHCARD_PROMPT_TEMPLATE = """You are a flashcard generator. Given the following study notes, create flashcards in JSON format.

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

class LlmClient:
    """Client for interacting with OpenAI LLM for flashcard generation"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
    
    def generate_flashcards(self, notes):
        """Generate flashcards from study notes"""
        # Format the prompt with user's notes
        prompt = FLASHCARD_PROMPT_TEMPLATE.format(notes=notes)
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
            
            # Extract raw response
            raw_content = response.choices[0].message.content.strip()
            
            # Parse JSON and return
            flashcards = json.loads(raw_content)
            return flashcards
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error generating flashcards: {str(e)}")
