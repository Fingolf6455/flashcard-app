import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LlmClient:
    """Client for interacting with OpenAI LLM"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
    
    def generate_flashcards(self, prompt):
        """Generate flashcards using OpenAI API"""
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
