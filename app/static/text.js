const socket = io();

const textForm = document.getElementById('text-form');
const textInput = document.getElementById('text-input');
const receivedText = document.getElementById('received-text');
const processingIndicator = document.getElementById('processing-indicator');

textForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const text = textInput.value.trim();
    if (text) {
        const userText = document.createElement('p');
        userText.textContent = text;
        userText.className = 'user-text';
        received
