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
    e.dataTransfer.setData('text/plain', this.getAttribute('data-lead-id'));
    
    console.log(`Started dragging card ${this.getAttribute('data-lead-id')}`);
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
