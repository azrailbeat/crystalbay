/**
 * Drag and Drop functionality for leads kanban board
 * 
 * This module handles the drag and drop functionality for lead cards on the Kanban board.
 * It allows users to move leads between different status columns visually, which also
 * updates the lead status in the backend via API calls.
 * 
 * @module drag-and-drop
 * @author Crystal Bay Travel
 * @version 1.3.0
 */

/**
 * Configuration and constants
 * @namespace Config
 */
const CONFIG = {
    /**
     * CSS selectors used throughout the module
     * @memberof Config
     */
    selectors: {
        leadCard: '.lead-card',
        leadCardWithoutId: '.lead-card:not([data-lead-id])',
        leadList: '.lead-list',
        kanbanColumn: '.kanban-column',
        columnCount: '.column-count',
        leadActions: '.lead-actions',
        newLeadBtn: '.new-lead-btn',
        modal: '#viewLeadModal',
    },
    
    /**
     * CSS classes used for visual effects
     * @memberof Config
     */
    classes: {
        dragging: 'dragging',
        dropTarget: 'drop-target',
        leadTag: 'lead-tag',
        borderSuccess: 'border-success',
    },
    
    /**
     * API endpoints
     * @memberof Config
     */
    api: {
        updateStatus: '/api/leads/{id}/status',
        fetchLead: '/api/leads/{id}',
        fetchInteractions: '/api/leads/{id}/interactions',
    },
    
    /**
     * Timing for animations and effects (in milliseconds)
     * @memberof Config
     */
    timing: {
        visualFeedback: 1000,
        toastDisplay: 5000,
    },
    
    /**
     * Status mapping for column indices
     * @memberof Config
     */
    statusMapping: [
        { id: 'new', name: 'Новый' },
        { id: 'in_progress', name: 'В работе' },
        { id: 'negotiation', name: 'Переговоры' },
        { id: 'booked', name: 'Забронировано' },
        { id: 'canceled', name: 'Отменено' }
    ]
};

// Global variables for drag and drop state
let draggedCard = null;

/**
 * Initialize all drag and drop functionality
 */
function initDragAndDrop() {
    console.log('Initializing drag and drop...');
    
    try {
        // Clean any existing event listeners first
        cleanupExistingListeners();
        
        // Setup card drag events
        setupCardDragEvents();
        
        // Setup column drop events
        setupColumnDropEvents();
        
        // Update column counts initially
        updateColumnCounts();
        
        console.log('Drag and drop initialized successfully');
    } catch (error) {
        console.error('Error initializing drag and drop:', error);
    }
}

/**
 * Clean up any existing event listeners (useful for re-initialization)
 */
function cleanupExistingListeners() {
    try {
        // Remove drag and drop listeners from cards
        document.querySelectorAll(CONFIG.selectors.leadCard).forEach(card => {
            card.removeAttribute('draggable');
            
            // Clone to remove all event listeners
            const clone = card.cloneNode(true);
            if (card.parentNode) {
                card.parentNode.replaceChild(clone, card);
            }
        });
        
        // Remove listeners from columns
        document.querySelectorAll(CONFIG.selectors.leadList).forEach(list => {
            const clone = list.cloneNode(false);
            
            // Move all children to the clone
            while (list.firstChild) {
                clone.appendChild(list.firstChild);
            }
            
            if (list.parentNode) {
                list.parentNode.replaceChild(clone, list);
            }
        });
        
        console.log('Existing event listeners cleaned up');
    } catch (error) {
        console.error('Error cleaning up event listeners:', error);
    }
}

/**
 * Set up drag events on all lead cards
 */
function setupCardDragEvents() {
    try {
        const cards = document.querySelectorAll(CONFIG.selectors.leadCard);
        console.log(`Found ${cards.length} cards to make draggable`);
        
        cards.forEach((card, index) => {
            // Ensure each card has an ID
            if (!card.hasAttribute('data-lead-id')) {
                const cardId = `temp-${index}`;
                card.setAttribute('data-lead-id', cardId);
                console.log(`Added temporary ID ${cardId} to card`);
            }
            
            // Make the card draggable
            card.setAttribute('draggable', 'true');
            
            // Add drag event listeners
            card.addEventListener('dragstart', handleCardDragStart);
            card.addEventListener('dragend', handleCardDragEnd);
            
            // Add click event for viewing details
            card.addEventListener('click', handleCardClick);
            
            console.log(`Card ${card.getAttribute('data-lead-id')} is now draggable`);
        });
    } catch (error) {
        console.error('Error setting up card drag events:', error);
    }
}

/**
 * Set up drop events on all columns
 */
function setupColumnDropEvents() {
    try {
        const columns = document.querySelectorAll(CONFIG.selectors.leadList);
        console.log(`Found ${columns.length} columns for drop targets`);
        
        columns.forEach((column, index) => {
            column.addEventListener('dragover', handleColumnDragOver);
            column.addEventListener('dragenter', handleColumnDragEnter);
            column.addEventListener('dragleave', handleColumnDragLeave);
            column.addEventListener('drop', handleColumnDrop);
            console.log(`Column ${index} is now a drop target`);
        });
    } catch (error) {
        console.error('Error setting up column drop events:', error);
    }
}

/**
 * Handle the start of dragging a card
 * @param {DragEvent} e - The drag event
 */
function handleCardDragStart(e) {
    try {
        // Don't start drag if clicking on action buttons
        if (e.target.closest(CONFIG.selectors.leadActions) || 
            e.target.tagName === 'BUTTON' || 
            e.target.closest('button')) {
            e.preventDefault();
            return false;
        }
        
        // Store reference to dragged card
        draggedCard = this;
        
        // Add visual effect
        this.classList.add(CONFIG.classes.dragging);
        
        // Store card ID in the data transfer
        const leadId = this.getAttribute('data-lead-id');
        e.dataTransfer.setData('text/plain', leadId);
        e.dataTransfer.effectAllowed = 'move';
        
        console.log(`Started dragging card ${leadId}`);
        
        // Opacity effect with delay
        setTimeout(() => {
            if (this && this.style) {
                this.style.opacity = '0.4';
            }
        }, 0);
        
        return true;
    } catch (error) {
        console.error('Error in card drag start handler:', error);
        return false;
    }
}

/**
 * Handle the end of dragging a card
 * @param {DragEvent} e - The drag event
 */
function handleCardDragEnd(e) {
    try {
        // Reset visual appearance
        this.classList.remove(CONFIG.classes.dragging);
        
        if (this && this.style) {
            this.style.opacity = '';
        }
        
        // Remove drop target highlights
        document.querySelectorAll(CONFIG.selectors.leadList).forEach(list => {
            list.classList.remove(CONFIG.classes.dropTarget);
        });
        
        console.log('Card drag ended');
    } catch (error) {
        console.error('Error in card drag end handler:', error);
    }
}

/**
 * Handle dragover event on columns (needed to allow drops)
 * @param {DragEvent} e - The drag event
 */
function handleColumnDragOver(e) {
    e.preventDefault();
    return false;
}

/**
 * Handle dragenter event on columns (for visual feedback)
 * @param {DragEvent} e - The drag event
 */
function handleColumnDragEnter(e) {
    this.classList.add(CONFIG.classes.dropTarget);
}

/**
 * Handle dragleave event on columns (for visual feedback)
 * @param {DragEvent} e - The drag event
 */
function handleColumnDragLeave(e) {
    this.classList.remove(CONFIG.classes.dropTarget);
}

/**
 * Handle drop event on columns
 * @param {DragEvent} e - The drag event
 */
function handleColumnDrop(e) {
    try {
        e.preventDefault();
        e.stopPropagation();
        
        // Remove visual feedback
        this.classList.remove(CONFIG.classes.dropTarget);
        
        // Get the card ID from the data transfer
        const leadId = e.dataTransfer.getData('text/plain');
        if (!leadId || !draggedCard) {
            console.error('Missing lead ID or dragged card reference');
            return false;
        }
        
        // Get source and target columns
        const sourceColumn = draggedCard.closest(CONFIG.selectors.kanbanColumn);
        const targetColumn = this.closest(CONFIG.selectors.kanbanColumn);
        
        if (!sourceColumn || !targetColumn) {
            console.error('Could not determine source or target column');
            return false;
        }
        
        // Only move between different columns
        if (sourceColumn !== targetColumn) {
            console.log('Moving card between columns');
            
            // Get column indices
            const columns = Array.from(document.querySelectorAll(CONFIG.selectors.kanbanColumn));
            const sourceIndex = columns.indexOf(sourceColumn);
            const targetIndex = columns.indexOf(targetColumn);
            
            // Get the new status based on target column
            const newStatus = getStatusByColumnIndex(targetIndex);
            console.log(`Moving from column ${sourceIndex} to ${targetIndex}, new status: ${newStatus}`);
            
            // Move the card in the DOM
            const dropList = this;
            const addButton = dropList.querySelector(CONFIG.selectors.newLeadBtn);
            
            if (addButton) {
                dropList.insertBefore(draggedCard, addButton);
            } else {
                dropList.appendChild(draggedCard);
            }
            
            // Update column counts
            updateColumnCounts();
            
            // Show visual feedback
            showSuccessIndicator(draggedCard);
            
            // Update the status on the server
            updateLeadStatus(leadId, newStatus);
        } else {
            console.log('Same column drop, not moving');
        }
        
        return false;
    } catch (error) {
        console.error('Error in column drop handler:', error);
        return false;
    }
}

/**
 * Handle click on a lead card to show details
 * @param {MouseEvent} e - The click event
 */
function handleCardClick(e) {
    try {
        // Don't open modal if clicking buttons or action area
        if (e.target.closest(CONFIG.selectors.leadActions) || 
            e.target.tagName === 'BUTTON' || 
            e.target.closest('button')) {
            return;
        }
        
        const leadId = this.getAttribute('data-lead-id');
        console.log(`Card clicked, opening details for lead ID: ${leadId}`);
        
        // Show modal with lead data
        openLeadModal(leadId);
    } catch (error) {
        console.error('Error handling card click:', error);
    }
}

/**
 * Open the lead details modal
 * @param {string} leadId - The ID of the lead to show
 */
function openLeadModal(leadId) {
    try {
        const modalElement = document.getElementById('viewLeadModal');
        if (!modalElement) {
            console.error('Modal element not found');
            return;
        }
        
        // Store the lead ID in the modal
        modalElement.setAttribute('data-lead-id', leadId);
        
        // Create and show the Bootstrap modal
        const modal = new bootstrap.Modal(modalElement);
        
        // Update the modal content
        updateModalContent(leadId, modalElement);
        
        // Show the modal
        modal.show();
    } catch (error) {
        console.error('Error opening lead modal:', error);
    }
}

/**
 * Update the content of the modal with lead data
 * @param {string} leadId - The ID of the lead
 * @param {HTMLElement} modalElement - The modal element
 */
async function updateModalContent(leadId, modalElement) {
    try {
        // Set a loading state
        modalElement.querySelector('.modal-title').textContent = 'Загрузка...';
        
        // Fetch lead data
        const leadData = await fetchLeadData(leadId);
        
        if (leadData) {
            // Update modal title and basic info
            modalElement.querySelector('.modal-title').textContent = leadData.customer_name || 'Без имени';
            
            // Update other fields if they exist
            const fields = {
                '.lead-source-info': leadData.source || 'Неизвестный источник',
                '.lead-email': leadData.customer_email || 'Нет данных',
                '.lead-phone': leadData.customer_phone || 'Нет данных',
                '.lead-status': getStatusName(leadData.status),
                '.lead-created': formatDate(leadData.created_at),
                '.lead-notes': leadData.notes || 'Нет заметок'
            };
            
            // Update each field if it exists in the modal
            Object.entries(fields).forEach(([selector, value]) => {
                const element = modalElement.querySelector(selector);
                if (element) {
                    element.textContent = value;
                }
            });
            
            // Fetch and display interactions
            loadLeadInteractions(leadId, modalElement);
        } else {
            modalElement.querySelector('.modal-title').textContent = 'Ошибка загрузки';
        }
    } catch (error) {
        console.error('Error updating modal content:', error);
        modalElement.querySelector('.modal-title').textContent = 'Ошибка загрузки';
    }
}

/**
 * Fetch lead data from the API
 * @param {string} leadId - The ID of the lead
 * @returns {Promise<object|null>} The lead data or null if an error occurs
 */
async function fetchLeadData(leadId) {
    try {
        const url = CONFIG.api.fetchLead.replace('{id}', leadId);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.lead;
    } catch (error) {
        console.error('Error fetching lead data:', error);
        showToast('Ошибка загрузки данных обращения', 'danger');
        return null;
    }
}

/**
 * Load and display lead interactions in the modal
 * @param {string} leadId - The ID of the lead
 * @param {HTMLElement} modalElement - The modal element
 */
async function loadLeadInteractions(leadId, modalElement) {
    try {
        const url = CONFIG.api.fetchInteractions.replace('{id}', leadId);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        const interactionsList = modalElement.querySelector('.comment-list');
        
        if (interactionsList && data.interactions && data.interactions.length > 0) {
            interactionsList.innerHTML = '';
            
            data.interactions.forEach(interaction => {
                const interactionHtml = createInteractionHtml(interaction);
                interactionsList.insertAdjacentHTML('beforeend', interactionHtml);
            });
        } else if (interactionsList) {
            interactionsList.innerHTML = '<div class="no-interactions">Нет истории взаимодействий</div>';
        }
    } catch (error) {
        console.error('Error loading interactions:', error);
        showToast('Ошибка загрузки взаимодействий', 'danger');
    }
}

/**
 * Create HTML for a single interaction
 * @param {object} interaction - The interaction data
 * @returns {string} HTML string for the interaction
 */
function createInteractionHtml(interaction) {
    const date = formatDate(interaction.created_at);
    const author = interaction.agent_name || 'Система';
    const initials = getInitials(author);
    
    // Special styling for AI interactions
    const isAiAnalysis = interaction.type === 'ai_analysis';
    const aiClass = isAiAnalysis ? 'ai-interaction' : '';
    
    return `
        <div class="comment-item ${aiClass}">
            <div class="comment-header">
                <span class="lead-avatar ${isAiAnalysis ? 'ai-avatar' : ''}">
                    ${isAiAnalysis ? '<i class="bi bi-cpu"></i>' : initials}
                </span>
                <span class="comment-author">${author}</span>
                <span class="comment-date">${date}</span>
            </div>
            <div class="comment-content">
                ${formatInteractionNotes(interaction.notes)}
            </div>
        </div>
    `;
}

/**
 * Get initials from a name
 * @param {string} name - The name to get initials from
 * @returns {string} The initials
 */
function getInitials(name) {
    if (!name) return '??';
    
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
    }
    
    return name.substring(0, 2).toUpperCase();
}

/**
 * Format interaction notes with HTML line breaks
 * @param {string} notes - The notes to format
 * @returns {string} Formatted notes
 */
function formatInteractionNotes(notes) {
    if (!notes) return 'Нет данных';
    return notes.replace(/\n/g, '<br>');
}

/**
 * Format a date string for display
 * @param {string} dateStr - The date string
 * @returns {string} Formatted date
 */
function formatDate(dateStr) {
    if (!dateStr) return 'Нет даты';
    
    try {
        const date = new Date(dateStr);
        return new Intl.DateTimeFormat('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    } catch (error) {
        console.error('Error formatting date:', error);
        return dateStr;
    }
}

/**
 * Update the lead status on the server
 * @param {string} leadId - The ID of the lead
 * @param {string} newStatus - The new status
 */
async function updateLeadStatus(leadId, newStatus) {
    try {
        const url = CONFIG.api.updateStatus.replace('{id}', leadId);
        
        // Notify that update is in progress
        showToast(`Обновление статуса обращения #${leadId}...`, 'info');
        
        // Send API request
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
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
 * Show visual success indicator on a card
 * @param {HTMLElement} card - The card element
 */
function showSuccessIndicator(card) {
    if (!card) return;
    
    card.classList.add(CONFIG.classes.borderSuccess);
    setTimeout(() => {
        card.classList.remove(CONFIG.classes.borderSuccess);
    }, CONFIG.timing.visualFeedback);
}

/**
 * Update the count displays in all columns
 */
/**
 * Update the count of cards in each column and handle empty state visualization
 */
function updateColumnCounts() {
    try {
        document.querySelectorAll(CONFIG.selectors.kanbanColumn).forEach((column, index) => {
            const leadList = column.querySelector(CONFIG.selectors.leadList);
            const cardsCount = column.querySelectorAll(CONFIG.selectors.leadCard).length;
            const countEl = column.querySelector(CONFIG.selectors.columnCount);
            
            // Update the count display
            if (countEl) {
                countEl.textContent = cardsCount;
            }
            
            // Add empty state indicator if there are no cards in the column
            if (cardsCount === 0 && leadList) {
                // Check if empty state message already exists
                let emptyStateMsg = leadList.querySelector('.empty-column-message');
                
                // Only add message if it doesn't already exist and there's no "new lead" button
                if (!emptyStateMsg && !leadList.querySelector(CONFIG.selectors.newLeadBtn)) {
                    emptyStateMsg = document.createElement('div');
                    emptyStateMsg.className = 'empty-column-message text-muted text-center p-3';
                    emptyStateMsg.innerHTML = '<em>Нет запросов</em>';
                    leadList.appendChild(emptyStateMsg);
                }
            } else {
                // Remove empty state message if there are cards
                const emptyStateMsg = leadList && leadList.querySelector('.empty-column-message');
                if (emptyStateMsg) {
                    emptyStateMsg.remove();
                }
            }
            
            console.log(`Column ${index} now has ${cardsCount} cards`);
        });
    } catch (error) {
        console.error('Error updating column counts:', error);
    }
}

/**
 * Get status code by column index
 * @param {number} index - Column index
 * @returns {string} Status code
 */
function getStatusByColumnIndex(index) {
    return CONFIG.statusMapping[index]?.id || 'new';
}

/**
 * Get status display name by status code
 * @param {string} statusCode - Status code
 * @returns {string} Status display name
 */
function getStatusName(statusCode) {
    const status = CONFIG.statusMapping.find(s => s.id === statusCode);
    return status ? status.name : 'Неизвестный';
}

/**
 * Show a toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, info, warning, danger)
 */
function showToast(message, type = 'info') {
    try {
        // Check if showToast function is defined globally
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            // Create a toast if global function doesn't exist
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            document.body.appendChild(toast);
            
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: CONFIG.timing.toastDisplay
            });
            
            bsToast.show();
            
            // Remove from DOM after hiding
            toast.addEventListener('hidden.bs.toast', () => {
                document.body.removeChild(toast);
            });
        }
    } catch (error) {
        console.error('Error showing toast:', error);
    }
}

// Initialize drag and drop when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('DOM loaded, initializing drag and drop');
        initDragAndDrop();
        
        // Show initial page load notification
        setTimeout(() => {
            const totalCards = document.querySelectorAll(CONFIG.selectors.leadCard).length;
            showToast(`Загружено ${totalCards} обращений`, 'info');
        }, 500);
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});

// Expose functions for external use
window.kanbanBoard = {
    initDragAndDrop,
    openLeadModal,
    updateColumnCounts,
    showToast
};