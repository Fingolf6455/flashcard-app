"""
Simple validation utilities for flashcard data
"""


def is_valid_card(card):
    """Naive validation - just check basic structure"""
    if not isinstance(card, dict):
        return False

    # Must have question and answer
    if "question" not in card or "answer" not in card:
        return False

    # Must not be empty
    if not card["question"].strip() or not card["answer"].strip():
        return False

    return True


def is_valid(cards):
    """Simple validation for flashcard set"""
    if not isinstance(cards, list) or len(cards) == 0:
        return False

    for card in cards:
        if not is_valid_card(card):
            return False

    return True
