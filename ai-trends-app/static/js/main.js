// Main JavaScript utilities and shared functions

// Show/Hide loading spinner
function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

// Toast notification system
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    toast.className = `${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
    toast.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, 5000);
}

// API request helper
async function makeRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('Request error:', error);
        throw error;
    }
}

// Format text with markdown-like styling
function formatText(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
        .replace(/\n/g, '<br>');
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    });
}

// Email integration
function composeEmail(subject, body) {
    const emailBody = encodeURIComponent(body);
    const emailSubject = encodeURIComponent(subject);
    
    // Create modal for email options
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-semibold mb-4">Send Email</h3>
            <p class="text-gray-600 mb-6">Choose your preferred email client:</p>
            <div class="space-y-3">
                <a href="mailto:?subject=${emailSubject}&body=${emailBody}" 
                   class="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-3 px-4 rounded-lg transition duration-200">
                    <i class="fas fa-envelope mr-2"></i>Default Email Client
                </a>
                <a href="https://mail.google.com/mail/?view=cm&su=${emailSubject}&body=${emailBody}" 
                   target="_blank"
                   class="block w-full bg-red-600 hover:bg-red-700 text-white text-center py-3 px-4 rounded-lg transition duration-200">
                    <i class="fab fa-google mr-2"></i>Gmail
                </a>
                <a href="https://outlook.live.com/mail/0/deeplink/compose?subject=${emailSubject}&body=${emailBody}" 
                   target="_blank"
                   class="block w-full bg-blue-800 hover:bg-blue-900 text-white text-center py-3 px-4 rounded-lg transition duration-200">
                    <i class="fab fa-microsoft mr-2"></i>Outlook
                </a>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    class="mt-4 w-full bg-gray-300 hover:bg-gray-400 text-gray-700 py-2 px-4 rounded-lg transition duration-200">
                Cancel
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Trends Dashboard loaded');
});