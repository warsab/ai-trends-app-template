
// ============================================================================
// AI TRENDZ DASHBOARD - Main JavaScript
// ============================================================================

// ============================================================================
// QUOTES SYSTEM
// ============================================================================

// You can add more quotes to this array:
const quotes = [
    { text: "Artificial Intelligence is the new electricity.", author: "Andrew Ng" },
    { text: "The question of whether a computer can think is no more interesting than the question of whether a submarine can swim.", author: "Edsger W. Dijkstra" },
    { text: "AI is probably the most important thing humanity has ever worked on. I think of it as something more profound than electricity or fire.", author: "Sundar Pichai" },
    { text: "Machine learning is the last invention that humanity will ever need to make.", author: "Nick Bostrom" },
    { text: "The key to artificial intelligence has always been the representation.", author: "Jeff Hawkins" },
    { text: "AI doesn't have to be evil to destroy humanity – if AI has a goal and humanity just happens to come in the way, it will destroy humanity as a matter of course without even thinking about it, no hard feelings.", author: "Elon Musk" },
    { text: "Success in creating AI would be the biggest event in human history. Unfortunately, it might also be the last.", author: "Stephen Hawking" },
    { text: "The real question is, when will we draft an artificial intelligence bill of rights? What will that consist of? And who will get to decide that?", author: "Gray Scott" },
    { text: "By far, the greatest danger of Artificial Intelligence is that people conclude too early that they understand it.", author: "Eliezer Yudkowsky" },
    { text: "AI is not going to replace humans, but humans with AI are going to replace humans without AI.", author: "Karim Lakhani" }
];

let currentQuoteIndex = -1;

function changeQuote() {
    let newIndex;
    do {
        newIndex = Math.floor(Math.random() * quotes.length);
    } while (newIndex === currentQuoteIndex && quotes.length > 1);
    
    currentQuoteIndex = newIndex;
    const quote = quotes[currentQuoteIndex];
    
    const quoteText = document.getElementById('quoteText');
    const quoteAuthor = document.getElementById('quoteAuthor');
    
    if (!quoteText || !quoteAuthor) return;
    
    quoteText.classList.remove('quote-animate');
    quoteAuthor.classList.remove('quote-animate');
    
    setTimeout(() => {
        quoteText.textContent = `"${quote.text}"`;
        quoteAuthor.textContent = `— ${quote.author}`;
        
        quoteText.classList.add('quote-animate');
        quoteAuthor.classList.add('quote-animate');
    }, 100);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    
    const colors = {
        success: 'bg-green-500/80 border-green-400',
        error: 'bg-red-500/80 border-red-400',
        warning: 'bg-yellow-500/80 border-yellow-400',
        info: 'bg-emerald-500/80 border-emerald-400'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.className = `${colors[type]} backdrop-blur-sm border-2 text-white px-6 py-4 rounded-lg shadow-2xl transform transition-all duration-300 translate-x-full`;
    toast.innerHTML = `
        <div class="flex items-center justify-between">
            <span><i class="fas ${icons[type]} mr-2"></i>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => toast.classList.remove('translate-x-full'), 100);
    
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function showLoading(text = 'Processing...') {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingText = document.getElementById('loadingText');
    
    if (loadingSpinner) {
        loadingText.textContent = text;
        loadingSpinner.classList.remove('hidden');
    }
}

function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.classList.add('hidden');
    }
}

// ============================================================================
// REPORT GENERATION
// ============================================================================

async function generateReport() {
    showLoading('Generating your personalized AI trends report...');
    
    try {
        const response = await fetch('/generate-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showToast('Report generated successfully!', 'success');
            displayReport(data.report);
        } else {
            showToast(data.error || 'Failed to generate report', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error generating report. Please try again.', 'error');
        console.error('Error:', error);
    }
}

function displayReport(reportMarkdown) {
    const reportContent = document.getElementById('reportContent');
    const reportModal = document.getElementById('reportModal');
    
    if (!reportContent || !reportModal) return;
    
    // Convert markdown to HTML (simple conversion)
    reportContent.innerHTML = convertMarkdownToHTML(reportMarkdown);
    reportModal.classList.remove('hidden');
}

function closeReportModal() {
    const reportModal = document.getElementById('reportModal');
    if (reportModal) {
        reportModal.classList.add('hidden');
    }
}

function copyReport() {
    const reportContent = document.getElementById('reportContent');
    if (!reportContent) return;
    
    const reportText = reportContent.innerText;
    navigator.clipboard.writeText(reportText).then(() => {
        showToast('Report copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy report', 'error');
    });
}

// Simple markdown to HTML converter
function convertMarkdownToHTML(markdown) {
    let html = markdown;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-xl font-bold text-white mt-6 mb-3">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-2xl font-bold text-white mt-8 mb-4">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold text-white mt-10 mb-5">$1</h1>');
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-emerald-300">$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-emerald-400 hover:text-emerald-300 underline" target="_blank">$1</a>');
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    // Horizontal rules
    html = html.replace(/---/g, '<hr class="border-emerald-500/30 my-6">');
    
    return html;
}

// ============================================================================
// AI LEADERBOARD
// ============================================================================

async function generateLeaderboard() {
    showLoading('Generating AI Leaderboard visualization...');
    
    try {
        const response = await fetch('/generate-leaderboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            if (data.filename) {
                showToast('Opening leaderboard...', 'success');
                window.open(`/leaderboard/${data.filename}`, '_blank');
            } else {
                showToast('Leaderboard is being generated. Please check back in a moment...', 'info');
                // Poll for the file after a delay
                setTimeout(checkLeaderboardStatus, 5000);
            }
        } else {
            showToast(data.error || 'Failed to generate leaderboard', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error generating leaderboard. Please try again.', 'error');
        console.error('Error:', error);
    }
}

async function checkLeaderboardStatus() {
    try {
        const response = await fetch('/generate-leaderboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success && data.filename) {
            showToast('Leaderboard ready!', 'success');
            window.open(`/leaderboard/${data.filename}`, '_blank');
        }
    } catch (error) {
        console.error('Error checking leaderboard status:', error);
    }
}

// ============================================================================
// AI CHATBOT
// ============================================================================

let chatHistory = [];

function openChatbot() {
    // Create chat modal
    const chatModal = document.createElement('div');
    chatModal.id = 'chatModal';
    chatModal.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4';
    chatModal.innerHTML = `
        <div class="glass-card rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div class="p-6 border-b border-emerald-500/30 flex justify-between items-center">
                <h2 class="text-2xl font-bold text-white">
                    <i class="fas fa-robot text-emerald-400 mr-2"></i>AI Assistant
                </h2>
                <button onclick="closeChatModal()" class="text-gray-400 hover:text-white transition">
                    <i class="fas fa-times text-2xl"></i>
                </button>
            </div>
            <div id="chatMessages" class="flex-1 overflow-y-auto p-6 space-y-4">
                <div class="text-gray-400 text-center text-sm">
                    <i class="fas fa-comment-dots mb-2"></i>
                    <p>Ask me anything about AI trends!</p>
                </div>
            </div>
            <div class="p-6 border-t border-emerald-500/30">
                <div class="flex space-x-2">
                    <input type="text" id="chatInput" placeholder="Type your message..." 
                           class="flex-1 bg-black/30 border border-emerald-500/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500"
                           onkeypress="if(event.key === 'Enter') sendChatMessage()">
                    <button onclick="sendChatMessage()" 
                            class="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 px-6 py-3 rounded-lg border border-emerald-500/50 transition">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(chatModal);
}

function closeChatModal() {
    const modal = document.getElementById('chatModal');
    if (modal) {
        modal.remove();
        chatHistory = []; // Reset chat history when closing
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingId = addChatMessage('Thinking...', 'assistant', true);
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        const typingElement = document.getElementById(typingId);
        if (typingElement) typingElement.remove();
        
        if (data.success) {
            addChatMessage(data.message, 'assistant');
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push({ role: 'assistant', content: data.message });
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    } catch (error) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) typingElement.remove();
        addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        console.error('Chat error:', error);
    }
}

function addChatMessage(message, role, isTyping = false) {
    const messagesContainer = document.getElementById('chatMessages');
    if (!messagesContainer) return null;
    
    const messageId = 'msg-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const bubble = document.createElement('div');
    bubble.className = `max-w-[80%] rounded-2xl px-4 py-3 ${
        role === 'user' 
            ? 'bg-emerald-500/20 text-emerald-100 border border-emerald-500/50' 
            : 'bg-gray-700/50 text-gray-100 border border-gray-600/50'
    }`;
    
    if (isTyping) {
        bubble.innerHTML = '<i class="fas fa-circle-notch fa-spin mr-2"></i>Thinking...';
    } else {
        bubble.textContent = message;
    }
    
    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

// ============================================================================
// LINKEDIN POST GENERATOR
// ============================================================================

function generateLinkedInPost() {
    // Create LinkedIn modal
    const linkedinModal = document.createElement('div');
    linkedinModal.id = 'linkedinModal';
    linkedinModal.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4';
    linkedinModal.innerHTML = `
        <div class="glass-card rounded-2xl shadow-2xl max-w-2xl w-full">
            <div class="p-6 border-b border-orange-500/30">
                <h2 class="text-2xl font-bold text-white">
                    <i class="fab fa-linkedin text-orange-400 mr-2"></i>Generate LinkedIn Post
                </h2>
            </div>
            <div class="p-6">
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">Choose Option:</label>
                        <div class="space-y-2">
                            <label class="flex items-center p-3 bg-black/30 rounded-lg border border-orange-500/30 cursor-pointer hover:bg-black/50 transition">
                                <input type="radio" name="linkedinOption" value="from_report" checked class="mr-3">
                                <span class="text-white">Generate from my latest report</span>
                            </label>
                            <label class="flex items-center p-3 bg-black/30 rounded-lg border border-orange-500/30 cursor-pointer hover:bg-black/50 transition">
                                <input type="radio" name="linkedinOption" value="custom_topic" class="mr-3">
                                <span class="text-white">Custom topic</span>
                            </label>
                        </div>
                    </div>
                    <div id="customTopicInput" class="hidden">
                        <label class="block text-sm font-medium text-gray-300 mb-2">Enter Topic:</label>
                        <input type="text" id="linkedinTopic" placeholder="e.g., Latest developments in LLMs" 
                               class="w-full bg-black/30 border border-orange-500/30 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-orange-500">
                    </div>
                </div>
            </div>
            <div class="p-6 border-t border-orange-500/30 flex justify-end space-x-4">
                <button onclick="closeLinkedInModal()" class="bg-gray-500/20 hover:bg-gray-500/30 text-gray-300 px-6 py-2 rounded-lg border border-gray-500/50 transition">
                    Cancel
                </button>
                <button onclick="submitLinkedInPost()" class="bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 px-6 py-2 rounded-lg border border-orange-500/50 transition">
                    <i class="fas fa-magic mr-2"></i>Generate
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(linkedinModal);
    
    // Toggle custom topic input
    const radioButtons = document.querySelectorAll('input[name="linkedinOption"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            const customInput = document.getElementById('customTopicInput');
            if (this.value === 'custom_topic') {
                customInput.classList.remove('hidden');
            } else {
                customInput.classList.add('hidden');
            }
        });
    });
}

function closeLinkedInModal() {
    const modal = document.getElementById('linkedinModal');
    if (modal) modal.remove();
}

async function submitLinkedInPost() {
    const selectedOption = document.querySelector('input[name="linkedinOption"]:checked');
    if (!selectedOption) return;
    
    const option = selectedOption.value;
    const topicInput = document.getElementById('linkedinTopic');
    const topic = topicInput ? topicInput.value.trim() : '';
    
    if (option === 'custom_topic' && !topic) {
        showToast('Please enter a topic', 'warning');
        return;
    }
    
    closeLinkedInModal();
    showLoading('Generating your LinkedIn post...');
    
    try {
        const response = await fetch('/generate-linkedin-post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ option, topic })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showToast('LinkedIn post generated!', 'success');
            displayLinkedInPost(data.post);
        } else {
            showToast(data.error || 'Failed to generate post', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error generating post. Please try again.', 'error');
        console.error('Error:', error);
    }
}

function displayLinkedInPost(post) {
    const postModal = document.createElement('div');
    postModal.id = 'postDisplayModal';
    postModal.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4';
    postModal.innerHTML = `
        <div class="glass-card rounded-2xl shadow-2xl max-w-2xl w-full">
            <div class="p-6 border-b border-orange-500/30">
                <h2 class="text-2xl font-bold text-white">
                    <i class="fab fa-linkedin text-orange-400 mr-2"></i>Your LinkedIn Post
                </h2>
            </div>
            <div class="p-6">
                <div class="bg-black/30 rounded-lg p-4 border border-orange-500/30 whitespace-pre-wrap text-gray-100 max-h-96 overflow-y-auto">
${post}
                </div>
            </div>
            <div class="p-6 border-t border-orange-500/30 flex justify-end space-x-4">
                <button onclick="copyLinkedInPost()" class="bg-gray-500/20 hover:bg-gray-500/30 text-gray-300 px-6 py-2 rounded-lg border border-gray-500/50 transition">
                    <i class="fas fa-copy mr-2"></i>Copy
                </button>
                <button onclick="postToLinkedIn()" class="bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 px-6 py-2 rounded-lg border border-orange-500/50 transition">
                    <i class="fab fa-linkedin mr-2"></i>Post to LinkedIn
                </button>
                <button onclick="closePostDisplayModal()" class="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 px-6 py-2 rounded-lg border border-emerald-500/50 transition">
                    <i class="fas fa-check mr-2"></i>Done
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(postModal);
    window.currentLinkedInPost = post;
}

function closePostDisplayModal() {
    const modal = document.getElementById('postDisplayModal');
    if (modal) modal.remove();
}

function copyLinkedInPost() {
    if (!window.currentLinkedInPost) return;
    
    navigator.clipboard.writeText(window.currentLinkedInPost).then(() => {
        showToast('Post copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy post', 'error');
    });
}

function postToLinkedIn() {
    if (!window.currentLinkedInPost) return;
    
    // Copy to clipboard first
    navigator.clipboard.writeText(window.currentLinkedInPost).then(() => {
        showToast('Post copied! Opening LinkedIn...', 'success');
        
        // Open LinkedIn in new tab
        // LinkedIn's create post URL
        window.open('https://www.linkedin.com/feed/?shareActive=true', '_blank');
        
        // Show helper message
        setTimeout(() => {
            showToast('Paste your post (Ctrl+V / Cmd+V) on LinkedIn', 'info');
        }, 1000);
    }).catch(() => {
        showToast('Failed to copy post', 'error');
    });
}

// ============================================================================
// YOUTUBE VIDEOS
// ============================================================================

async function getYouTubeVideos() {
    showLoading('Finding personalized AI videos for you...');
    
    try {
        const response = await fetch('/get-youtube-videos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        hideLoading();
        
        if (data.success) {
            showToast(`Found ${data.videos.length} videos!`, 'success');
            displayYouTubeVideos(data.videos, data.keywords);
        } else {
            showToast(data.error || 'Failed to fetch videos', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error fetching videos. Please try again.', 'error');
        console.error('Error:', error);
    }
}

function displayYouTubeVideos(videos, keywords) {
    const videoModal = document.createElement('div');
    videoModal.id = 'videoModal';
    videoModal.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4';
    
    const videosHTML = videos.map(video => `
        <a href="${video.url}" target="_blank" class="block bg-black/30 rounded-lg border border-pink-500/30 hover:border-pink-500/50 transition overflow-hidden group">
            <div class="relative">
                <img src="${video.thumbnail}" alt="${escapeHtml(video.title)}" class="w-full h-48 object-cover">
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                    <i class="fas fa-play-circle text-white text-5xl"></i>
                </div>
            </div>
            <div class="p-4">
                <h3 class="text-white font-semibold mb-2 line-clamp-2">${escapeHtml(video.title)}</h3>
                <p class="text-gray-400 text-sm mb-2">${escapeHtml(video.channel)}</p>
                <p class="text-gray-500 text-xs line-clamp-2">${escapeHtml(video.description)}</p>
            </div>
        </a>
    `).join('');
    
    videoModal.innerHTML = `
        <div class="glass-card rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div class="p-6 border-b border-pink-500/30">
                <div class="flex justify-between items-center">
                    <div>
                        <h2 class="text-2xl font-bold text-white">
                            <i class="fab fa-youtube text-pink-400 mr-2"></i>AI Video Recommendations
                        </h2>
                        <p class="text-gray-400 text-sm mt-1">Based on: ${escapeHtml(keywords)}</p>
                    </div>
                    <button onclick="closeVideoModal()" class="text-gray-400 hover:text-white transition">
                        <i class="fas fa-times text-2xl"></i>
                    </button>
                </div>
            </div>
            <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${videosHTML}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(videoModal);
}

function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    if (modal) modal.remove();
}

// Helper function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded successfully!');
    
    // Load initial quote
    changeQuote();
    
    // Add event listeners if needed
    // Additional initialization code here
});