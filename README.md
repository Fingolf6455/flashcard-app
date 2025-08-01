# Flashcard App

A simple flashcard app that uses OpenAI to generate study cards from your notes. Uses spaced repetition to help you remember stuff better.

## How to Run

```bash
pip install flask openai
python app.py
```

Go to http://localhost:5000

## What it does

- Paste in your study notes
- AI creates flashcards automatically  
- Shows you cards when you need to review them
- Keeps track of what you know vs what you're still learning

## Requirements

- Python 3.8+
- Flask
- OpenAI API key

## Todo

- Add deck organization
- CSV import/export
- Better scheduling algorithm
