// ResearchMate AI - Frontend JavaScript

// Global state
let currentSessionId = null;
let isLoading = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('ResearchMate AI - Web UI initialized');
    loadConversations();
    setupTextareaAutoResize();
    focusInput();
});

// ============================================================
// Message Sending
// ============================================================

async function sendMessage(event) {
    if (event) event.preventDefault();

    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message || isLoading) return;

    // Clear input immediately
    input.value = '';
    input.style.height = 'auto';

    // Hide welcome message if present
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.style.display = 'none';

    // Add user message to UI
    addMessageToUI('user', message);

    // Show loading indicator
    showLoadingIndicator();
    isLoading = true;
    updateSendButton(false);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update current session ID
        if (!currentSessionId) {
            currentSessionId = data.session_id;
        }

        // Remove loading indicator
        hideLoadingIndicator();

        // Add assistant response to UI with quality score if available
        addMessageToUI('assistant', data.response, data.quality_report);

        // Refresh conversation list to show updated timestamp and current session
        loadConversations();

    } catch (error) {
        console.error('Error sending message:', error);
        hideLoadingIndicator();
        addMessageToUI('assistant', `❌ Error: ${error.message}\n\nPlease try again or check the server logs.`);
    } finally {
        isLoading = false;
        updateSendButton(true);
        focusInput();
    }
}

function setQuery(query) {
    const input = document.getElementById('messageInput');
    input.value = query;
    input.focus();
    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ============================================================
// UI Message Handling
// ============================================================

function addMessageToUI(role, content, qualityReport = null) {
    const messagesContainer = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = role === 'user' ? 'You' : 'AI';
    const avatarInitial = role === 'user' ? 'U' : 'R';

    // Add quality badge if available
    let qualityBadge = '';
    if (qualityReport && qualityReport.overall_score !== undefined) {
        const score = qualityReport.overall_score;
        const grade = qualityReport.grade;
        let badgeColor = '#10b981'; // Green for A
        if (score < 90) badgeColor = '#3b82f6'; // Blue for B
        if (score < 80) badgeColor = '#f59e0b'; // Orange for C
        if (score < 70) badgeColor = '#ef4444'; // Red for D/F

        qualityBadge = `
            <div class="quality-badge" style="background: ${badgeColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-left: 8px;" title="Quality Score: ${score}/100 - ${qualityReport.summary.passed}/${qualityReport.summary.total_checks} checks passed">
                ${grade} ${score}/100
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${avatarInitial}</div>
            <div class="message-author">${avatar}</div>
            ${qualityBadge}
        </div>
        <div class="message-content" id="msg-${Date.now()}"></div>
    `;

    messagesContainer.appendChild(messageDiv);

    const contentDiv = messageDiv.querySelector('.message-content');

    if (role === 'assistant') {
        // Render markdown for assistant messages
        contentDiv.innerHTML = marked.parse(content, {
            breaks: true,
            gfm: true
        });

        // Highlight code blocks
        contentDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });

        // Make links open in new tab
        contentDiv.querySelectorAll('a').forEach((link) => {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        });
    } else {
        // Plain text for user messages
        contentDiv.textContent = content;
    }

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showLoadingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">R</div>
            <div class="message-author">AI</div>
        </div>
        <div class="loading-indicator">
            <span>Researching</span>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function updateSendButton(enabled) {
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = !enabled;
}

// ============================================================
// Conversation Management
// ============================================================

async function loadConversations() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();

        const conversationList = document.getElementById('conversationList');
        conversationList.innerHTML = '';

        if (data.sessions.length === 0) {
            conversationList.innerHTML = '<p style="text-align: center; color: var(--text-tertiary); padding: 20px; font-size: 13px;">No conversations yet</p>';
            return;
        }

        data.sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            if (session.id === currentSessionId) {
                item.classList.add('active');
            }

            const date = new Date(session.updated_at);
            const formattedDate = formatDate(date);

            item.innerHTML = `
                <div class="conversation-content" style="flex: 1; min-width: 0;">
                    <div class="conversation-title">${escapeHtml(session.title)}</div>
                    <div class="conversation-date">${formattedDate}</div>
                </div>
                <button class="delete-conversation-btn" title="Delete conversation" data-session-id="${session.id}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            `;

            // Click on conversation content loads session
            const contentDiv = item.querySelector('.conversation-content');
            contentDiv.onclick = () => loadSession(session.id);

            // Click on delete button deletes session
            const deleteBtn = item.querySelector('.delete-conversation-btn');
            deleteBtn.onclick = (e) => {
                e.stopPropagation(); // Prevent loading session
                deleteConversation(session.id, session.title);
            };

            conversationList.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

async function loadSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        const data = await response.json();

        currentSessionId = sessionId;

        // Clear chat messages
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = '';

        // Load messages
        data.messages.forEach(msg => {
            // Extract quality report from metadata if available (for assistant messages)
            let qualityReport = null;
            if (msg.role === 'assistant' && msg.metadata) {
                const score = msg.metadata.quality_score;
                const grade = msg.metadata.quality_grade;
                if (score !== undefined && score !== null) {
                    qualityReport = {
                        overall_score: score,
                        grade: grade || 'N/A',
                        summary: {
                            passed: 0,
                            total_checks: 0
                        }
                    };
                }
            }
            addMessageToUI(msg.role, msg.content, qualityReport);
        });

        // Update session title
        document.getElementById('sessionTitle').textContent = data.session.title;

        // Update active state in sidebar
        loadConversations();

    } catch (error) {
        console.error('Error loading session:', error);
    }
}

async function deleteConversation(sessionId, sessionTitle) {
    // Confirm deletion
    const confirmed = confirm(`Are you sure you want to delete "${sessionTitle}"?\n\nThis action cannot be undone.`);
    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`/api/sessions/${sessionId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete conversation');
        }

        console.log(`Deleted conversation: ${sessionId}`);

        // If deleted conversation was currently active, start a new chat
        if (sessionId === currentSessionId) {
            newChat();
        }

        // Reload conversation list
        loadConversations();

    } catch (error) {
        console.error('Error deleting conversation:', error);
        alert('Failed to delete conversation. Please try again.');
    }
}

function newChat() {
    currentSessionId = null;

    // Clear chat messages
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="50" cy="50" r="45" fill="#4F46E5" opacity="0.1"/>
                    <path d="M 30 30 L 40 50 L 35 50 L 35 70 L 65 70 L 65 50 L 60 50 L 70 30 Z" fill="#4F46E5"/>
                    <circle cx="50" cy="40" r="8" fill="#818CF8"/>
                    <rect x="32" y="70" width="36" height="4" fill="#4F46E5"/>
                </svg>
            </div>
            <h2>Welcome to ResearchMate AI</h2>
            <p>Your intelligent research assistant with verified sources and citations.</p>
            <div class="example-queries">
                <h3>Try asking:</h3>
                <button class="example-btn" onclick="setQuery('What are the best wireless headphones under $250?')">
                    🎧 Best wireless headphones under $250?
                </button>
                <button class="example-btn" onclick="setQuery('Compare Toyota Camry vs Honda Accord 2024')">
                    🚗 Compare Toyota Camry vs Honda Accord 2024
                </button>
                <button class="example-btn" onclick="setQuery('Help me get started with astrophotography')">
                    🔭 Getting started with astrophotography
                </button>
            </div>
        </div>
    `;

    // Update title
    document.getElementById('sessionTitle').textContent = 'New Conversation';

    // Reload conversations to clear active state
    loadConversations();

    // Focus input
    focusInput();
}

// ============================================================
// Utility Functions
// ============================================================

function formatDate(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setupTextareaAutoResize() {
    const textarea = document.getElementById('messageInput');

    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });

    // Handle Enter key
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function focusInput() {
    const input = document.getElementById('messageInput');
    input.focus();
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// ============================================================
// Markdown Configuration
// ============================================================

// Configure marked.js
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
});

console.log('✅ ResearchMate AI loaded successfully');
