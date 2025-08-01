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
            resultDiv.innerHTML = '<h3>Generated Flashcards:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
    })
    .catch(error => {
        resultDiv.innerHTML = '<h3>Error:</h3><pre>Network error: ' + error.message + '</pre>';
    });
}
