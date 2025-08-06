"""
Unit tests for llm_client.py - Testing LLM client with mocked OpenAI API
"""
import pytest
import json
from unittest.mock import Mock, patch
from llm_client import LlmClient, FLASHCARD_PROMPT_TEMPLATE


class TestLlmClientInitialization:
    """Unit tests for LlmClient initialization"""
    
    @patch('llm_client.os.getenv')
    @patch('llm_client.openai')
    def test_init_sets_api_key(self, mock_openai, mock_getenv):
        """Test that LlmClient properly initializes with API key"""
        mock_getenv.return_value = 'test-api-key'
        
        client = LlmClient()
        
        mock_getenv.assert_called_once_with('OPENAI_API_KEY')
        assert client.api_key == 'test-api-key'
        assert mock_openai.api_key == 'test-api-key'
    
    @patch('llm_client.os.getenv')
    def test_init_with_no_api_key(self, mock_getenv):
        """Test LlmClient initialization when no API key is set"""
        mock_getenv.return_value = None
        
        client = LlmClient()
        
        assert client.api_key is None


class TestFlashcardGeneration:
    """Unit tests for flashcard generation with mocked OpenAI responses"""
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_generate_flashcards_success(self, mock_getenv, mock_openai_create):
        """Test successful flashcard generation with mocked OpenAI response"""
        # Setup mocks
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([
            {
                "question": "What is Python?",
                "answer": "A programming language",
                "hint": "Think about snakes",
                "tags": ["programming", "python"]
            }
        ])
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        notes = "Python is a programming language"
        
        result = client.generate_flashcards(notes)
        
        # Verify OpenAI was called correctly
        mock_openai_create.assert_called_once()
        call_args = mock_openai_create.call_args
        assert call_args[1]['model'] == 'gpt-4o'
        assert call_args[1]['max_completion_tokens'] == 1000
        assert call_args[1]['temperature'] == 1
        
        # Verify messages structure
        messages = call_args[1]['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert notes in messages[1]['content']
        
        # Verify result
        expected = [{
            "question": "What is Python?",
            "answer": "A programming language", 
            "hint": "Think about snakes",
            "tags": ["programming", "python"]
        }]
        assert result == expected
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_generate_flashcards_json_decode_error(self, mock_getenv, mock_openai_create):
        """Test handling of invalid JSON response from OpenAI"""
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response {"
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        
        with pytest.raises(ValueError) as exc_info:
            client.generate_flashcards("test notes")
        
        assert "Failed to parse AI response as JSON" in str(exc_info.value)
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_generate_flashcards_openai_api_error(self, mock_getenv, mock_openai_create):
        """Test handling of OpenAI API errors"""
        mock_getenv.return_value = 'test-api-key'
        mock_openai_create.side_effect = Exception("API rate limit exceeded")
        
        client = LlmClient()
        
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_flashcards("test notes")
        
        assert "Error generating flashcards" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_generate_flashcards_multiple_cards(self, mock_getenv, mock_openai_create):
        """Test generation of multiple flashcards"""
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([
            {"question": "Q1", "answer": "A1", "tags": ["tag1"]},
            {"question": "Q2", "answer": "A2", "tags": ["tag2"]},
            {"question": "Q3", "answer": "A3", "tags": ["tag3"]}
        ])
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        result = client.generate_flashcards("test notes")
        
        assert len(result) == 3
        assert result[0]['question'] == 'Q1'
        assert result[1]['question'] == 'Q2' 
        assert result[2]['question'] == 'Q3'


class TestPromptTemplateFormatting:
    """Unit tests for prompt template formatting"""
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_prompt_contains_user_notes(self, mock_getenv, mock_openai_create):
        """Test that user notes are properly included in the prompt"""
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '[]'
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        test_notes = "Water boils at 100 degrees Celsius"
        
        client.generate_flashcards(test_notes)
        
        # Check that the prompt was formatted with user notes
        call_args = mock_openai_create.call_args
        user_message = call_args[1]['messages'][1]['content']
        assert test_notes in user_message
        assert "Notes to process:" in user_message
    
    def test_prompt_template_structure(self):
        """Test that the prompt template has expected structure"""
        test_notes = "Test notes content"
        formatted_prompt = FLASHCARD_PROMPT_TEMPLATE.format(notes=test_notes)
        
        # Check key elements are in the prompt
        assert "flashcard generator" in formatted_prompt.lower()
        assert "JSON format" in formatted_prompt
        assert "question" in formatted_prompt
        assert "answer" in formatted_prompt
        assert "hint" in formatted_prompt
        assert "tags" in formatted_prompt
        assert test_notes in formatted_prompt
        assert "photosynthesis" in formatted_prompt  # Example in template


class TestEdgeCasesAndErrorHandling:
    """Unit tests for edge cases and error conditions"""
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_empty_notes_input(self, mock_getenv, mock_openai_create):
        """Test handling of empty notes input"""
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '[]'
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        result = client.generate_flashcards("")
        
        # Should still make API call, even with empty notes
        mock_openai_create.assert_called_once()
        assert result == []
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_very_long_notes_input(self, mock_getenv, mock_openai_create):
        """Test handling of very long notes input"""
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '[]'
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        long_notes = "This is a test. " * 1000  # Very long input
        
        result = client.generate_flashcards(long_notes)
        
        # Should handle long input gracefully
        mock_openai_create.assert_called_once()
        call_args = mock_openai_create.call_args
        user_message = call_args[1]['messages'][1]['content']
        assert long_notes in user_message
    
    @patch('llm_client.openai.ChatCompletion.create')
    @patch('llm_client.os.getenv')
    def test_unicode_notes_input(self, mock_getenv, mock_openai_create):
        """Test handling of unicode characters in notes"""
        mock_getenv.return_value = 'test-api-key'
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([{
            "question": "What is café?",
            "answer": "Coffee ☕",
            "tags": ["français"]
        }])
        mock_openai_create.return_value = mock_response
        
        client = LlmClient()
        unicode_notes = "Le café est délicieux "
        
        result = client.generate_flashcards(unicode_notes)
        
        assert result[0]['question'] == "What is café?"
        assert result[0]['answer'] == "Coffee ☕"
