/**
 * Drag and Drop functionality for leads kanban board
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing drag and drop functionality');
    initDragAndDrop();
});

// Store for currently dragged card
let draggedItem = null;

/**
 * Initialize drag and drop for all lead cards
 */
function initDragAndDrop() {
    // Add ID to cards that don't have one
    const cardsWithoutId = document.querySelectorAll('.lead-card:not([data-lead-id])');
    console.log(`Adding IDs to ${cardsWithoutId.length} cards without data-lead-id`);
    
    cardsWithoutId.forEach((card, index) => {
        const cardId = 1000 + index;
        card.setAttribute('data-lead-id', cardId);
        console.log(`Added ID ${cardId} to card`);
    });
    
    // Get all cards
    const cards = document.querySelectorAll('.lead-card');
    console.log(`Found ${cards.length} cards to initialize`);
    
    // Setup drag handlers for each card
    cards.forEach(card => {
        card.setAttribute('draggable', 'true');
        
        // Add drag start and end event listeners
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        
        // Modify card to handle clicks for viewing details separately from drag
        setupCardForClicks(card);
        
        console.log(`Card ${card.getAttribute('data-lead-id')} initialized for drag`);
    });
    
    // Setup drop targets (the columns)
    const columns = document.querySelectorAll('.lead-list');
    console.log(`Found ${columns.length} columns to set as drop targets`);
    
    columns.forEach((column, index) => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('dragenter', handleDragEnter);
        column.addEventListener('dragleave', handleDragLeave);
        column.addEventListener('drop', handleDrop);
        console.log(`Column ${index} initialized for drop`);
    });
    
    // Update column counts initially
    updateColumnCounts();
    console.log('Drag and drop initialization complete');
}

/**
 * Handle the start of drag
 */
function handleDragStart(e) {
    // Skip if dragging from buttons or actions
    if (e.target.closest('.lead-actions') || e.target.tagName === 'BUTTON' || e.target.closest('button')) {
        console.log('Ignoring drag from button or action');
        e.preventDefault();
        e.stopPropagation();
        return false;
    }
    
    // Store the dragged card reference
    draggedItem = this;
    
    // Add visual effect
    this.classList.add('dragging');
    setTimeout(() => {
        this.style.opacity = '0.4';
    }, 0);
    
    // Set data for transfer
    e.dataTransfer.effectAllowed = 'move';
    const leadId = this.getAttribute('data-lead-id');
    e.dataTransfer.setData('text/plain', leadId || 'undefined');
    
    console.log(`Started dragging card ${leadId}`);
    return true;
}

/**
 * Handle the end of drag
 */
function handleDragEnd(e) {
    // Remove visual effects
    this.classList.remove('dragging');
    this.style.opacity = '1';
    
    // Remove drop target highlighting from all columns
    document.querySelectorAll('.lead-list').forEach(column => {
        column.classList.remove('drop-target');
    });
    
    console.log('Drag ended');
}

/**
 * Handle drag over event (needed to allow drops)
 */
function handleDragOver(e) {
    // Prevent default to allow drop
    e.preventDefault();
    return false;
}

/**
 * Handle drag enter event
 */
function handleDragEnter(e) {
    // Add highlight to show this is a valid drop target
    this.classList.add('drop-target');
}

/**
 * Handle drag leave event
 */
function handleDragLeave(e) {
    // Remove highlight
    this.classList.remove('drop-target');
}

/**
 * Handle drop event
 */
function handleDrop(e) {
    // Prevent default browser behavior
    e.preventDefault();
    e.stopPropagation();
    
    // Remove highlight
    this.classList.remove('drop-target');
    
    // Get the dragged card ID
    const leadId = e.dataTransfer.getData('text/plain');
    console.log(`Drop detected for lead ID: ${leadId}`);
    
    if (!draggedItem) {
        console.error('No card being dragged');
        return false;
    }
    
    try {
        // Get source and target columns
        const sourceColumn = draggedItem.closest('.kanban-column');
        const targetColumn = this.closest('.kanban-column');
        
        if (!sourceColumn || !targetColumn) {
            console.error('Could not determine source or target column');
            return false;
        }
        
        // Only move if dropping in a different column
        if (sourceColumn !== targetColumn) {
            console.log('Moving card between different columns');
            
            // Get column indexes to determine status
            const columns = Array.from(document.querySelectorAll('.kanban-column'));
            const sourceIndex = columns.indexOf(sourceColumn);
            const targetIndex = columns.indexOf(targetColumn);
            
            console.log(`Moving from column ${sourceIndex} to ${targetIndex}`);
            
            // Map column index to status
            const newStatus = getStatusByColumnIndex(targetIndex);
            console.log(`New status will be: ${newStatus}`);
            
            // Add card to the new column (before the 'add' button if it exists)
            const addButton = this.querySelector('.new-lead-btn');
            if (addButton) {
                this.insertBefore(draggedItem, addButton);
            } else {
                this.appendChild(draggedItem);
            }
            
            // Update column counts
            updateColumnCounts();
            
            // Send API request to update the status
            updateLeadStatus(leadId, newStatus);
            
            // Show confirmation toast
            showToast(`Карточка перемещена в статус "${getStatusName(newStatus)}"`, 'success');
        } else {
            console.log('Same column drop, not moving');
        }
    } catch (error) {
        console.error('Error handling drop:', error);
    }
    
    return false;
}

/**
 * Setup card for handling clicks separate from drag
 */
function setupCardForClicks(card) {
    // Remove modal triggers
    card.removeAttribute('data-bs-toggle');
    card.removeAttribute('data-bs-target');
    
    // Add click handler for opening modal
    card.addEventListener('click', function(e) {
        // Don't open modal if clicking buttons or actions
        if (e.target.closest('.lead-actions') || e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            return;
        }
        
        // Get lead ID and open modal
        const leadId = this.getAttribute('data-lead-id');
        console.log(`Card clicked, opening modal for lead ID: ${leadId}`);
        openLeadModal(leadId);
    });
}

/**
 * Map column index to status code
 */
function getStatusByColumnIndex(index) {
    const statusMap = [
        'new',            // 0 - Новые
        'in_progress',    // 1 - В работе
        'negotiation',    // 2 - Переговоры
        'booked',         // 3 - Забронировано
        'canceled'        // 4 - Отменено
    ];
    
    return statusMap[index] || 'new';
}

/**
 * Map status code to display name
 */
function getStatusName(status) {
    const statusMap = {
        'new': 'Новый',
        'in_progress': 'В работе',
        'negotiation': 'Переговоры',
        'booked': 'Забронировано',
        'canceled': 'Отменено',
        'pending': 'В ожидании',
        'confirmed': 'Подтвержден',
        'closed': 'Закрыт'
    };
    
    return statusMap[status] || status;
}

/**
 * Update card status via API
 */
async function updateLeadStatus(leadId, newStatus) {
    try {
        // Show status update notification
        showToast(`Обновление статуса обращения #${leadId}...`, 'info');
        
        // Send API request
        const response = await fetch(`/api/leads/${leadId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Статус обращения #${leadId} изменен на "${getStatusName(newStatus)}"`, 'success');
        } else {
            showToast(`Ошибка при обновлении статуса: ${data.error || 'Неизвестная ошибка'}`, 'danger');
        }
    } catch (error) {
        console.error('Error updating lead status:', error);
        showToast(`Ошибка при обновлении статуса: ${error.message}`, 'danger');
    }
}

/**
 * Update counts in all columns
 */
function updateColumnCounts() {
    document.querySelectorAll('.kanban-column').forEach((column, index) => {
        const countElement = column.querySelector('.column-count');
        if (countElement) {
            const cardsCount = column.querySelectorAll('.lead-card').length;
            countElement.textContent = cardsCount.toString();
            console.log(`Column ${index} now has ${cardsCount} cards`);
        }
    });
}

/**
 * Open lead details modal
 */
function openLeadModal(leadId) {
    const viewLeadModal = document.getElementById('viewLeadModal');
    if (!viewLeadModal) {
        console.error('Modal element not found');
        return;
    }
    
    const bsModal = new bootstrap.Modal(viewLeadModal);
    
    // Set lead ID in modal
    viewLeadModal.setAttribute('data-lead-id', leadId);
    
    // Show modal
    bsModal.show();
    
    // Load lead data
    fetchLeadData(leadId).then(data => {
        populateLeadModal(data);
    }).catch(error => {
        console.error('Error fetching lead data:', error);
        showToast('Ошибка загрузки данных обращения', 'danger');
    });
}

/**
 * Fetch lead data from API
 */
async function fetchLeadData(leadId) {
    try {
        const response = await fetch(`/api/leads/${leadId}`);
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching lead data:', error);
        throw error;
    }
}

/**
 * Populate lead modal with data
 */
function populateLeadModal(data) {
    const modal = document.getElementById('viewLeadModal');
    if (!modal || !data || !data.lead) {
        console.error('Modal element not found or invalid data');
        return;
    }
    
    const lead = data.lead;
    
    // Set modal title
    const titleEl = modal.querySelector('.modal-title');
    if (titleEl) {
        titleEl.textContent = `Обращение #${lead.id}: ${lead.name || 'Без имени'}`;
    }
    
    // Set lead details
    const nameEl = modal.querySelector('#lead-name');
    if (nameEl) nameEl.textContent = lead.name || 'Не указано';
    
    const emailEl = modal.querySelector('#lead-email');
    if (emailEl) emailEl.textContent = lead.email || 'Не указано';
    
    const phoneEl = modal.querySelector('#lead-phone');
    if (phoneEl) phoneEl.textContent = lead.phone || 'Не указано';
    
    const sourceEl = modal.querySelector('#lead-source');
    if (sourceEl) sourceEl.textContent = lead.source || 'Не указано';
    
    const dateEl = modal.querySelector('#lead-date');
    if (dateEl) dateEl.textContent = lead.created_at ? new Date(lead.created_at).toLocaleString() : 'Не указано';
    
    const statusSelect = modal.querySelector('#lead-status-select');
    if (statusSelect) statusSelect.value = lead.status || 'new';
    
    const detailsEl = modal.querySelector('#lead-details');
    if (detailsEl) detailsEl.textContent = lead.details || lead.message || 'Нет дополнительной информации';
    
    const tagsEl = modal.querySelector('#lead-tags');
    if (tagsEl) {
        tagsEl.innerHTML = '';
        if (lead.tags && lead.tags.length > 0) {
            lead.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'lead-tag me-2';
                tagSpan.textContent = tag;
                tagsEl.appendChild(tagSpan);
            });
        } else {
            tagsEl.textContent = 'Нет тегов';
        }
    }
    
    // Populate interactions
    const interactionsEl = modal.querySelector('#lead-interactions');
    if (interactionsEl) {
        interactionsEl.innerHTML = '';
        if (data.interactions && data.interactions.length > 0) {
            data.interactions.forEach(interaction => {
                const commentDiv = document.createElement('div');
                commentDiv.className = 'comment-item';
                
                const headerDiv = document.createElement('div');
                headerDiv.className = 'comment-header';
                
                const authorSpan = document.createElement('span');
                authorSpan.className = 'comment-author';
                authorSpan.textContent = interaction.user_name || 'Система';
                
                const dateSpan = document.createElement('span');
                dateSpan.className = 'comment-date';
                dateSpan.textContent = interaction.created_at ? new Date(interaction.created_at).toLocaleString() : 'Неизвестно';
                
                headerDiv.appendChild(authorSpan);
                headerDiv.appendChild(dateSpan);
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'comment-content';
                contentDiv.textContent = interaction.content || 'Пустое сообщение';
                
                commentDiv.appendChild(headerDiv);
                commentDiv.appendChild(contentDiv);
                
                interactionsEl.appendChild(commentDiv);
            });
        } else {
            interactionsEl.innerHTML = '<div class="text-center py-3">Нет записей о взаимодействиях</div>';
        }
    }
}

/**
 * Helper function to show toast notifications
 */
function showToast(message, type = 'info') {
    // Check if we already have a toast container
    let toastContainer = document.querySelector('.toast-container');
    
    // Create container if it doesn't exist
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Math.random().toString(36).substr(2, 9);
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type}`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.setAttribute('id', toastId);
    
    // Create toast content
    const toastContent = document.createElement('div');
    toastContent.className = 'd-flex';
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    
    toastContent.appendChild(toastBody);
    toastContent.appendChild(closeButton);
    toastEl.appendChild(toastContent);
    
    // Add toast to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    // Remove toast element after hiding
    toastEl.addEventListener('hidden.bs.toast', function () {
        toastEl.remove();
    });
}
