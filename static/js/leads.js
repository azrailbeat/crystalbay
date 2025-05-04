// Schedule periodic status check
function scheduleStatusCheck() {
    // Check for status updates every 5 minutes
    console.log('Setting up automatic status check every 5 minutes');
    // Disabled for development to avoid unnecessary API calls
    // setInterval(processAllLeads, 5 * 60 * 1000);
}

// Process all leads
async function processAllLeads() {
    try {
        showToast('Обрабатываю все обращения...', 'info');
        
        const response = await fetch('/api/leads/process-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Show success message with stats
        showToast(`Обработка завершена: обновлено ${data.updated} обращений`, 'success');
        
        // Reload the page to reflect the changes
        if (data.updated > 0) {
            setTimeout(() => {
                location.reload();
            }, 2000);
        }
        
    } catch (error) {
        console.error('Error processing all leads:', error);
        showToast('Ошибка обработки обращений', 'error');
    }
}

// Generic toast notification function
function showToast(message, type = 'info') {
    // Check if toast container exists, create if not
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    const toastBody = document.createElement('div');
    toastBody.className = 'd-flex';
    
    const toastContent = document.createElement('div');
    toastContent.className = 'toast-body';
    toastContent.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    
    // Assemble toast
    toastBody.appendChild(toastContent);
    toastBody.appendChild(closeButton);
    toastEl.appendChild(toastBody);
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    toast.show();
}