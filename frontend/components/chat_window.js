/**
 * Chat Window Component
 */
// Use global configuration (loaded from config.js)
// Ensure global variables are defined
if (typeof window.API_BASE === 'undefined') {
    window.API_BASE = 'http://localhost:8000';
}
if (typeof window.currentUserId === 'undefined') {
    window.currentUserId = 1;
}

function addMessage(content, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    
    // If this is the first message, remove welcome message
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    // Handle line breaks, preserve formatting
    const formattedContent = content.split('\n').map(line => {
        if (line.trim() === '') {
            return '<br>';
        }
        return line;
    }).join('<br>');
    
    messageDiv.innerHTML = formattedContent;
    chatMessages.appendChild(messageDiv);
    
    // Smooth scroll to bottom
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

async function sendMessage() {
    console.log('sendMessage function called');
    
    const messageInput = document.getElementById('messageInput');
    if (!messageInput) {
        console.error('Message input field not found');
        return;
    }
    
    const message = messageInput.value.trim();
    console.log('Input message:', message);
    
    if (!message) {
        console.log('Message is empty, not sending');
        return;
    }
    
    // Check if input is disabled
    if (messageInput.disabled) {
        console.warn('Input is disabled, cannot send message. Please start session first.');
        alert('Please click "Start Session" button first');
        return;
    }
    
    // Display user message
    addMessage(message, true);
    messageInput.value = '';
    
    // Temporarily disable input to prevent duplicate sends
    messageInput.disabled = true;
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
        sendBtn.disabled = true;
        const btnText = sendBtn.querySelector('.btn-text');
        if (btnText) {
            btnText.textContent = 'Sending...';
        } else {
            sendBtn.textContent = 'Sending...';
        }
    }
    
    try {
        const apiBase = window.API_BASE || 'http://localhost:8000';
        const userId = window.currentUserId || 1;
        console.log('Sending API request, user ID:', userId, 'message:', message);
        
        const response = await fetch(`${apiBase}/api/session/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: window.currentUserId || 1,
                message: message
            })
        });
        
        console.log('API response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(errorData.detail || `HTTP error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API response data:', data);
        
        if (data.success) {
            // Display assistant reply
            addMessage(data.response, false);
            
            // If session ended, show analysis result
            if (data.session_ended && data.analysis) {
                showAnalysisResult(data.analysis);
                disableChatInput();
                // Add ending message and return button
                setTimeout(() => {
                    addMessage('Today\'s conversation has ended. Thank you for sharing, and we\'ll see you next time. 💛', false);
                    // Show return button after 2 seconds
                    setTimeout(() => {
                        const returnBtn = document.createElement('div');
                        returnBtn.style.cssText = 'text-align: center; margin-top: 20px;';
                        returnBtn.innerHTML = '<a href="/" style="display: inline-block; padding: 12px 24px; background: var(--primary-blue); color: white; text-decoration: none; border-radius: 20px; font-size: 0.95em;">Back to Home</a>';
                        const chatMessages = document.getElementById('chatMessages');
                        chatMessages.appendChild(returnBtn);
                    }, 2000);
                }, 1000);
            } else {
                // Re-enable input
                messageInput.disabled = false;
                if (sendBtn) {
                    sendBtn.disabled = false;
                    const btnText = sendBtn.querySelector('.btn-text');
                    if (btnText) {
                        btnText.textContent = 'Share with your therapist';
                    } else {
                        sendBtn.textContent = 'Send';
                    }
                }
            }
        } else {
            console.error('Failed to send message, response data:', data);
            addMessage('Sorry, an error occurred while processing your message: ' + (data.detail || 'Unknown error'), false);
            // Re-enable input
            messageInput.disabled = false;
            if (sendBtn) {
                sendBtn.disabled = false;
                const btnText = sendBtn.querySelector('.btn-text');
                if (btnText) {
                    btnText.textContent = 'Share with your therapist';
                } else {
                    sendBtn.textContent = 'Send';
                }
            }
        }
    } catch (error) {
        console.error('Failed to send message:', error);
        addMessage('Network error: ' + error.message, false);
        // Re-enable input
        messageInput.disabled = false;
        if (sendBtn) {
            sendBtn.disabled = false;
            const btnText = sendBtn.querySelector('.btn-text');
            if (btnText) {
                btnText.textContent = 'Share with your therapist';
            } else {
                sendBtn.textContent = 'Send';
            }
        }
    }
}

function showAnalysisResult(analysis) {
    const analysisResult = document.getElementById('analysisResult');
    const analysisContent = document.getElementById('analysisContent');
    
    analysisContent.textContent = JSON.stringify(analysis, null, 2);
    analysisResult.style.display = 'block';
}

function enableChatInput() {
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendBtn').disabled = false;
}

function disableChatInput() {
    document.getElementById('messageInput').disabled = true;
    document.getElementById('sendBtn').disabled = true;
}

// Bind send button and input field events
function initChatWindow() {
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    
    if (sendBtn) {
        // Remove old event listeners (if any)
        const newSendBtn = sendBtn.cloneNode(true);
        sendBtn.parentNode.replaceChild(newSendBtn, sendBtn);
        
        // Bind new event listener
        newSendBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Send button clicked');
            sendMessage();
        });
        console.log('Send button event bound');
    } else {
        console.error('Send button not found');
    }
    
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('Enter key pressed, sending message');
                sendMessage();
            }
        });
        console.log('Input field event bound');
    } else {
        console.error('Message input field not found');
    }
}

// If DOM is already loaded, execute immediately; otherwise wait for DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatWindow);
} else {
    initChatWindow();
}

