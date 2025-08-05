function generateFlashcards() {
    const notes = document.getElementById('notes').value;
    if (!notes.trim()) {
        alert('Please enter some notes!');
        return;
    }
    
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<h3>Generating flashcards...</h3>';
    
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({notes: notes})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultDiv.innerHTML = '<h3>Error:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
        } else {
            displayFlashcards(data);
        }
    })
    .catch(error => {
        resultDiv.innerHTML = '<h3>Error:</h3><pre>Network error: ' + error.message + '</pre>';
    });
}

/**
 * Display generated flashcards in a beautiful card layout
 * @param {Array} flashcards - Array of flashcard objects from the API
 */
function displayFlashcards(flashcards) {
    const resultDiv = document.getElementById('result');
    
    // Handle empty results
    if (!flashcards || flashcards.length === 0) {
        resultDiv.innerHTML = '<h3>No flashcards generated</h3>';
        return;
    }
    
    let html = `
        <h3>Generated ${flashcards.length} Flashcard${flashcards.length > 1 ? 's' : ''}</h3>
        <div class="flashcards-container">
    `;
    
    // Build HTML for each flashcard
    flashcards.forEach((card, index) => {
        // Convert tags array to HTML spans
        const tags = card.tags && card.tags.length > 0 ? 
            card.tags.map(tag => `<span class="tag">${tag}</span>`).join('') : '';
        
        html += `
            <div class="flashcard" data-card-id="${card.id}">
                <div class="card-header">
                    <span class="card-number">Card ${index + 1}</span>
                    <span class="card-id">ID: ${card.id}</span>
                </div>
                
                <div class="card-content">
                    <div class="question-section">
                        <h4>Question:</h4>
                        <p>${card.question}</p>
                    </div>
                    
                    <div class="answer-section">
                        <h4>Answer:</h4>
                        <p class="answer blurred" onclick="revealAnswer(this)">${card.answer}</p>
                        <span class="reveal-hint">Click to reveal answer</span>
                    </div>
                    
                    ${card.hint ? `
                        <div class="hint-section">
                            <h4>Hint:</h4>
                            <p class="hint blurred" onclick="revealHint(this)">${card.hint}</p>
                            <span class="reveal-hint">Click to reveal hint</span>
                        </div>
                    ` : ''}
                    
                    ${tags ? `
                        <div class="tags-section">
                            <h4>Tags:</h4>
                            <div class="tags">${tags}</div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="card-actions">
                    <button onclick="startStudyMode(${card.id})">Study This Card</button>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="actions">
            <button onclick="startStudySession()">Study All Cards</button>
            <button onclick="viewAllSavedCards()">View All Saved Cards</button>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

function startStudyMode(cardId) {
    alert(`Study mode for card ${cardId} - Coming soon!`);
}

function startStudySession() {
    alert('Study session for all cards - Coming soon!');
}

/**
 * Reveal a blurred answer when clicked - core flashcard study functionality
 * @param {HTMLElement} element - The answer paragraph element that was clicked
 */
function revealAnswer(element) {
    element.classList.remove('blurred');
    element.classList.add('revealed');
    // Hide the "click to reveal" hint
    const hint = element.parentElement.querySelector('.reveal-hint');
    if (hint) hint.style.display = 'none';
}

/**
 * Reveal a blurred hint when clicked - helps with studying
 * @param {HTMLElement} element - The hint paragraph element that was clicked
 */
function revealHint(element) {
    element.classList.remove('blurred');
    element.classList.add('revealed');
    // Hide the "click to reveal" hint
    const hint = element.parentElement.querySelector('.reveal-hint');
    if (hint) hint.style.display = 'none';
}

/**
 * Fetch and display all saved cards from the database
 * Uses the GET /cards endpoint to retrieve all flashcards
 */
function viewAllSavedCards() {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<h3>Loading saved cards...</h3>';
    
    // Fetch all cards from the backend
    fetch('/cards')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultDiv.innerHTML = '<h3>Error:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } else if (data.length === 0) {
                resultDiv.innerHTML = '<h3>No saved cards yet</h3><p>Generate some flashcards first!</p>';
            } else {
                displaySavedCards(data);
            }
        })
        .catch(error => {
            resultDiv.innerHTML = '<h3>Error:</h3><pre>Network error: ' + error.message + '</pre>';
        });
}

/**
 * Display all saved cards in a grid layout with creation dates
 * @param {Array} cards - Array of saved card objects from database
 */
function displaySavedCards(cards) {
    const resultDiv = document.getElementById('result');
    
    let html = `
        <h3>All Saved Cards (${cards.length})</h3>
        <div class="flashcards-container">
    `;
    
    // Build HTML for each saved card
    cards.forEach((card, index) => {
        // Convert tags array to HTML spans
        const tags = card.tags && card.tags.length > 0 ? 
            card.tags.map(tag => `<span class="tag">${tag}</span>`).join('') : '';
        
        // Format creation date for display
        const createdDate = new Date(card.created_at).toLocaleDateString();
        
        html += `
            <div class="flashcard saved-card" data-card-id="${card.id}">
                <div class="card-header">
                    <span class="card-number">Card ${card.id}</span>
                    <span class="card-date">Created: ${createdDate}</span>
                </div>
                
                <div class="card-content">
                    <div class="question-section">
                        <h4>Question:</h4>
                        <p>${card.question}</p>
                    </div>
                    
                    <div class="answer-section">
                        <h4>Answer:</h4>
                        <p class="answer blurred" onclick="revealAnswer(this)">${card.answer}</p>
                        <span class="reveal-hint">Click to reveal answer</span>
                    </div>
                    
                    ${card.hint ? `
                        <div class="hint-section">
                            <h4>Hint:</h4>
                            <p class="hint blurred" onclick="revealHint(this)">${card.hint}</p>
                            <span class="reveal-hint">Click to reveal hint</span>
                        </div>
                    ` : ''}
                    
                    ${tags ? `
                        <div class="tags-section">
                            <h4>Tags:</h4>
                            <div class="tags">${tags}</div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="card-actions">
                    <button onclick="startStudyMode(${card.id})">Study This Card</button>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        <div class="actions">
            <button onclick="startStudySession()">Study All Cards</button>
            <button onclick="location.reload()">Generate New Cards</button>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}
