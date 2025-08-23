/**
 * Test functionality for the Kanban board
 * 
 * This module handles the test functionality for the leads Kanban board,
 * providing buttons to create test leads and reset all leads for testing.
 * 
 * @version 1.1.0
 * @updated 2025-05-06
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing test functionality for leads');
    
    // Initialize test buttons
    initTestButtons();
});

/**
 * Initialize test buttons for lead management
 */
function initTestButtons() {
    // Get button elements
    const createTestLeadBtn = document.getElementById('create-test-lead');
    const resetLeadsBtn = document.getElementById('reset-leads');
    
    // Add event listeners to buttons if they exist
    if (createTestLeadBtn) {
        createTestLeadBtn.addEventListener('click', createTestLead);
        console.log('Create test lead button initialized');
    }
    
    if (resetLeadsBtn) {
        resetLeadsBtn.addEventListener('click', resetAllLeads);
        console.log('Reset leads button initialized');
    }
}

/**
 * Create a test lead via API call
 */
function createTestLead() {
    console.log('Creating test lead');
    
    // Show loading indicator on button
    const button = document.getElementById('create-test-lead');
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="bi bi-hourglass-split"></i> Создаю...';
    button.disabled = true;
    
    // Make API call to create test lead
    fetch('/api/test/leads/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Test lead created successfully:', data);
        
        // Create and add the new lead card to the first column
        if (data.lead) {
            addNewLeadCardToDOM(data.lead);
        }
        
        // Show success state briefly
        button.innerHTML = '<i class="bi bi-check-circle"></i> Готово';
        
        // Reset button after delay
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.disabled = false;
        }, 1500);
    })
    .catch(error => {
        console.error('Error creating test lead:', error);
        
        // Show error state briefly
        button.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Ошибка';
        
        // Reset button after delay
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.disabled = false;
        }, 1500);
    });
}

/**
 * Reset all leads via API call
 */
function resetAllLeads() {
    console.log('Resetting all leads');
    
    // Show confirmation dialog
    if (!confirm('Вы уверены, что хотите удалить все карточки? Это действие нельзя отменить.')) {
        console.log('Reset cancelled by user');
        return;
    }
    
    // Show loading indicator on button
    const button = document.getElementById('reset-leads');
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="bi bi-hourglass-split"></i> Сбрасываю...';
    button.disabled = true;
    
    // Make API call to reset all leads
    fetch('/api/test/leads/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('All leads reset successfully:', data);
        
        // Remove all lead cards from DOM
        removeAllLeadCardsFromDOM();
        
        // Show success state briefly
        button.innerHTML = '<i class="bi bi-check-circle"></i> Готово';
        
        // Reset button after delay
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.disabled = false;
        }, 1500);
    })
    .catch(error => {
        console.error('Error resetting leads:', error);
        
        // Show error state briefly
        button.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Ошибка';
        
        // Reset button after delay
        setTimeout(() => {
            button.innerHTML = originalContent;
            button.disabled = false;
        }, 1500);
    });
}

/**
 * Add a new lead card to the DOM
 * 
 * @param {Object} lead - The lead data to add
 */
function addNewLeadCardToDOM(lead) {
    // Find the first column (new leads)
    const firstColumn = document.querySelector('.kanban-column:nth-child(1) .lead-list');
    if (!firstColumn) {
        console.error('Could not find first column to add lead card');
        return;
    }
    
    // Create new lead card element
    const newCard = document.createElement('div');
    newCard.className = 'lead-card';
    newCard.setAttribute('data-lead-id', lead.id);
    newCard.setAttribute('data-bs-toggle', 'modal');
    newCard.setAttribute('data-bs-target', '#viewLeadModal');
    
    // Create lead card content
    newCard.innerHTML = `
        <div class="lead-source">
            <i class="bi bi-robot source-icon"></i> Тестовая карточка
        </div>
        <div class="lead-name">${lead.customer_name || 'Тестовый клиент'}</div>
        <div class="lead-details">${lead.notes || 'Тестовый запрос для демонстрации функциональности Kanban-доски'}</div>
        <div class="lead-tags">
            ${lead.tags ? lead.tags.map(tag => `<span class="lead-tag">${tag}</span>`).join('') : '<span class="lead-tag">Тестовый тег</span><span class="lead-tag">Демо</span>'}
        </div>
        <div class="lead-footer">
            <div class="lead-date">только что</div>
            <div class="lead-actions">
                <button class="action-button" title="Добавить комментарий"><i class="bi bi-chat"></i></button>
                <button class="action-button" title="Обработать с AI"><i class="bi bi-robot"></i></button>
            </div>
        </div>
    `;
    
    // Insert at the top of the first column (before any other cards)
    const firstCard = firstColumn.querySelector('.lead-card');
    if (firstCard) {
        firstColumn.insertBefore(newCard, firstCard);
    } else {
        // Or add to the end if there are no cards
        firstColumn.appendChild(newCard);
    }
    
    // Update column count
    updateColumnCount(0);
    
    // Initialize drag functionality on the new card
    if (window.kanbanBoard && typeof window.kanbanBoard.initDragAndDrop === 'function') {
        // Run the kanban board initialization which will make all cards draggable
        window.kanbanBoard.initDragAndDrop();
    } else {
        console.warn('kanbanBoard.initDragAndDrop function not available, card may not be draggable');
    }
    
    // Add click event to open modal
    newCard.addEventListener('click', function() {
        console.log('Card clicked, opening details for lead ID:', lead.id);
    });
    
    // Flash the new card to highlight it
    setTimeout(() => {
        newCard.style.transition = 'background-color 0.5s ease';
        newCard.style.backgroundColor = '#e6f7ff';
        
        setTimeout(() => {
            newCard.style.backgroundColor = '';
        }, 1000);
    }, 100);
}

/**
 * Remove all lead cards from the DOM
 */
function removeAllLeadCardsFromDOM() {
    // Find all lead cards
    const allCards = document.querySelectorAll('.lead-card');
    
    // Remove each card with a brief fade animation
    allCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.transition = 'opacity 0.3s ease';
            card.style.opacity = '0';
            
            setTimeout(() => {
                card.remove();
                
                // Update column counts after all cards are removed
                if (index === allCards.length - 1) {
                    updateAllColumnCounts();
                }
            }, 300);
        }, index * 50); // Stagger removal for visual effect
    });
}

/**
 * Update the count display for a specific column
 * 
 * @param {number} columnIndex - The index of the column to update
 */
function updateColumnCount(columnIndex) {
    const column = document.querySelector(`.kanban-column:nth-child(${columnIndex + 1})`);
    if (!column) return;
    
    const countElement = column.querySelector('.column-count');
    if (!countElement) return;
    
    const cardCount = column.querySelectorAll('.lead-card').length;
    countElement.textContent = cardCount;
}

/**
 * Update the count displays for all columns
 */
function updateAllColumnCounts() {
    // Use the kanban board's updateColumnCounts function if available
    if (window.kanbanBoard && typeof window.kanbanBoard.updateColumnCounts === 'function') {
        window.kanbanBoard.updateColumnCounts();
        return;
    }
    
    // Fallback if the kanban board function is not available
    const columns = document.querySelectorAll('.kanban-column');
    
    columns.forEach((column, index) => {
        const countElement = column.querySelector('.column-count');
        if (!countElement) return;
        
        const cardCount = column.querySelectorAll('.lead-card').length;
        countElement.textContent = cardCount;
        
        // Handle empty state visualization
        const leadList = column.querySelector('.lead-list');
        if (cardCount === 0 && leadList) {
            // Check if empty state message already exists
            let emptyStateMsg = leadList.querySelector('.empty-column-message');
            
            // Only add message if it doesn't already exist
            if (!emptyStateMsg && !leadList.querySelector('.new-lead-btn')) {
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
    });
}