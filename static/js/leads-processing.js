/**
 * Lead processing functionality for Crystal Bay Travel
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing lead processing functionality');
    initAutoProcessButtons();
});

/**
 * Initialize buttons for auto-processing
 */
function initAutoProcessButtons() {
    // Start process button in modal
    const startProcessBtn = document.getElementById('start-process-btn');
    const stopProcessBtn = document.getElementById('stop-process-btn');
    
    if (startProcessBtn) {
        startProcessBtn.addEventListener('click', startAutoProcess);
        console.log('Process start button initialized');
    }
    
    if (stopProcessBtn) {
        stopProcessBtn.addEventListener('click', stopAutoProcess);
        console.log('Process stop button initialized');
    }
}

/**
 * Start the auto processing flow
 */
function startAutoProcess() {
    console.log('Starting auto-process of leads');
    
    // Show stop button, hide start button
    const startBtn = document.getElementById('start-process-btn');
    const stopBtn = document.getElementById('stop-process-btn');
    
    if (startBtn) startBtn.classList.add('d-none');
    if (stopBtn) stopBtn.classList.remove('d-none');
    
    // Reset UI
    updateProcessingUI('Начало обработки обращений...', 5);
    clearProcessLog();
    logProcessAction('Запуск автоматической обработки обращений');
    
    // Get process scope
    const scopeSelect = document.getElementById('process-scope');
    const scope = scopeSelect ? scopeSelect.value : 'new';
    
    // Get options
    const analyzeChecked = document.getElementById('analyze-check')?.checked || false;
    const categorizeChecked = document.getElementById('categorize-check')?.checked || false;
    const responseChecked = document.getElementById('response-check')?.checked || false;
    const statusChecked = document.getElementById('status-check')?.checked || false;
    const showAnimation = document.getElementById('show-animation')?.checked || false;
    
    // Log selected options
    logProcessAction(`Параметры обработки: ${scope === 'new' ? 'только новые' : scope === 'all' ? 'все активные' : 'выбранные'}`);
    
    if (analyzeChecked) logProcessAction('✓ Анализ содержимого включен');
    if (categorizeChecked) logProcessAction('✓ Категоризация включена');
    if (responseChecked) logProcessAction('✓ Подготовка ответов включена');
    if (statusChecked) logProcessAction('✓ Изменение статусов включено');
    
    // Start progress animation
    updateProcessingUI('Получение обращений для обработки...', 10);
    
    // Make API call to process all
    processAllInquiries(scope, {
        analyze: analyzeChecked,
        categorize: categorizeChecked,
        response: responseChecked,
        status: statusChecked,
        animation: showAnimation
    });
}

/**
 * Stop the auto processing flow
 */
function stopAutoProcess() {
    console.log('Stopping auto-process of leads');
    
    // Show start button, hide stop button
    const startBtn = document.getElementById('start-process-btn');
    const stopBtn = document.getElementById('stop-process-btn');
    
    if (stopBtn) stopBtn.classList.add('d-none');
    if (startBtn) startBtn.classList.remove('d-none');
    
    logProcessAction('Процесс остановлен пользователем');
    updateProcessingUI('Обработка остановлена', 0);
    
    // We would need to cancel any pending operations here if possible
    // For now, we just update the UI
}

/**
 * Call API to process all inquiries
 */
async function processAllInquiries(scope, options) {
    try {
        logProcessAction('Отправка запроса на обработку обращений...');
        
        // Show loading indicator
        showToast('Обработка обращений...', 'info');
        
        const response = await fetch('/api/leads/process-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scope: scope,
                options: options
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        updateProcessingUI('Получение результатов обработки...', 25);
        
        // Process results
        if (data.total === 0) {
            logProcessAction('Не найдено обращений для обработки');
            updateProcessingUI('Обработка завершена: нет обращений', 100);
            showToast('Не найдено обращений для обработки', 'warning');
            completeProcessing();
            return;
        }
        
        logProcessAction(`Найдено ${data.total} обращений для обработки`);
        
        // Process each result sequentially with visual updates
        const details = data.details || [];
        const total = details.length;
        let processed = 0;
        
        if (total === 0) {
            logProcessAction('Нет обращений требующих обработки');
            updateProcessingUI('Обработка завершена: нет обновлений', 100);
            showToast('Нет обращений требующих обработки', 'info');
            completeProcessing();
            return;
        }
        
        // Process in batches or one by one depending on animation option
        if (options.animation) {
            // Sequential processing with animation
            for (const detail of details) {
                await processLeadWithAnimation(detail);
                processed++;
                const progress = 25 + (processed / total * 75);
                updateProcessingUI(`Обработка ${processed} из ${total}...`, progress);
            }
        } else {
            // Process all at once without animation
            for (const detail of details) {
                logProcessAction(`Обработка обращения #${detail.lead_id}: ${detail.old_status} -> ${detail.new_status}`);
                // Quietly move cards without animation
                moveCardToNewStatus(detail.lead_id, detail.new_status);
                processed++;
                const progress = 25 + (processed / total * 75);
                updateProcessingUI(`Обработка ${processed} из ${total}...`, progress);
            }
            updateProcessingUI('Обработка завершена', 100);
            updateColumnCounts();
        }
        
        // Show summary
        const message = `Автоматическая обработка завершена. Обработано ${data.updated} обращений${data.failed > 0 ? `, ${data.failed} ошибок` : ''}.`;
        logProcessAction(message);
        showToast(message, 'success');
        completeProcessing();
        
    } catch (error) {
        console.error('Error processing inquiries:', error);
        logProcessAction(`Ошибка при обработке: ${error.message}`);
        updateProcessingUI('Обработка прервана из-за ошибки', 0);
        showToast(`Ошибка при обработке обращений: ${error.message}`, 'danger');
        completeProcessing();
    }
}

/**
 * Move a card to a new status column without animation
 */
function moveCardToNewStatus(leadId, newStatus) {
    const leadCard = document.querySelector(`.lead-card[data-lead-id="${leadId}"]`);
    if (!leadCard) {
        console.log(`Card for lead #${leadId} not found in the interface`);
        return false;
    }
    
    const targetColumnIndex = getColumnIndexByStatus(newStatus);
    const targetColumn = document.querySelector(`.kanban-column:nth-child(${targetColumnIndex + 1}) .lead-list`);
    
    if (!targetColumn) {
        console.log(`Target column for status ${newStatus} not found`);
        return false;
    }
    
    // Move the card
    const addButton = targetColumn.querySelector('.new-lead-btn');
    if (addButton) {
        targetColumn.insertBefore(leadCard, addButton);
    } else {
        targetColumn.appendChild(leadCard);
    }
    
    return true;
}

/**
 * Process a single lead with animation
 */
async function processLeadWithAnimation(detail) {
    return new Promise(resolve => {
        const leadId = detail.lead_id;
        const oldStatus = detail.old_status;
        const newStatus = detail.new_status;
        
        logProcessAction(`Обработка обращения #${leadId}...`);
        
        // Find the lead card
        const leadCard = document.querySelector(`.lead-card[data-lead-id="${leadId}"]`);
        if (!leadCard) {
            logProcessAction(`Карточка для обращения #${leadId} не найдена в интерфейсе`);
            setTimeout(resolve, 500); // Short delay for log readability
            return;
        }
        
        // If status changed, move the card
        if (oldStatus !== newStatus) {
            logProcessAction(`Изменение статуса #${leadId}: ${getStatusName(oldStatus)} -> ${getStatusName(newStatus)}`);
            
            // Get source and target columns
            const sourceColumn = document.querySelector(`.kanban-column:nth-child(${getColumnIndexByStatus(oldStatus) + 1}) .lead-list`);
            const targetColumn = document.querySelector(`.kanban-column:nth-child(${getColumnIndexByStatus(newStatus) + 1}) .lead-list`);
            
            if (sourceColumn && targetColumn && sourceColumn !== targetColumn) {
                // Highlight the card
                leadCard.style.boxShadow = '0 0 10px rgba(0, 123, 255, 0.7)';
                
                // Create a visual clone for animation
                const rect = leadCard.getBoundingClientRect();
                const clone = leadCard.cloneNode(true);
                clone.style.position = 'fixed';
                clone.style.width = rect.width + 'px';
                clone.style.top = rect.top + 'px';
                clone.style.left = rect.left + 'px';
                clone.style.zIndex = '9999';
                clone.style.opacity = '0.9';
                clone.style.pointerEvents = 'none';
                document.body.appendChild(clone);
                
                // Get target position
                const targetRect = targetColumn.getBoundingClientRect();
                const targetTop = targetRect.top + 20; // Padding
                const targetLeft = targetRect.left + 20; // Padding
                
                // Hide original during animation
                leadCard.style.opacity = '0';
                
                // Perform animation
                setTimeout(() => {
                    clone.style.transition = 'all 0.8s ease-in-out';
                    clone.style.top = targetTop + 'px';
                    clone.style.left = targetLeft + 'px';
                    
                    setTimeout(() => {
                        // Remove clone and show original in new position
                        document.body.removeChild(clone);
                        
                        // Move actual card
                        const addButton = targetColumn.querySelector('.new-lead-btn');
                        if (addButton) {
                            targetColumn.insertBefore(leadCard, addButton);
                        } else {
                            targetColumn.appendChild(leadCard);
                        }
                        
                        // Reset and show the original
                        leadCard.style.opacity = '1';
                        leadCard.style.boxShadow = '';
                        
                        // Update column counts
                        updateColumnCounts();
                        
                        // Complete
                        setTimeout(resolve, 200);
                    }, 800); // Match transition duration
                }, 100);
            } else {
                logProcessAction(`Невозможно переместить карточку #${leadId}: колонки не найдены`);
                setTimeout(resolve, 500);
            }
        } else {
            // Just update card data
            logProcessAction(`Обновление данных обращения #${leadId} без изменения статуса`);
            setTimeout(resolve, 800);
        }
    });
}

/**
 * Complete the processing flow
 */
function completeProcessing() {
    // Reset buttons
    const startBtn = document.getElementById('start-process-btn');
    const stopBtn = document.getElementById('stop-process-btn');
    
    if (stopBtn) stopBtn.classList.add('d-none');
    if (startBtn) startBtn.classList.remove('d-none');
}

/**
 * Clear the process log
 */
function clearProcessLog() {
    const log = document.getElementById('process-log');
    if (log) log.innerHTML = '';
}

/**
 * Update processing UI elements
 */
function updateProcessingUI(status, progress) {
    const statusEl = document.getElementById('process-status');
    const progressBar = document.getElementById('process-progress');
    
    // Update progress bar
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    // Update status text
    if (statusEl) statusEl.textContent = status;
}

/**
 * Log a process action to the UI
 */
function logProcessAction(message) {
    const log = document.getElementById('process-log');
    const timestamp = new Date().toLocaleTimeString();
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<small class="text-muted">${timestamp}</small> ${message}`;
    
    if (log) {
        log.appendChild(entry);
        log.scrollTop = log.scrollHeight; // Auto-scroll to bottom
    }
    
    console.log(`[Process] ${message}`);
}

/**
 * Get column index by status
 */
function getColumnIndexByStatus(status) {
    // Map status to column index
    const statusMap = {
        'new': 0,
        'in_progress': 1,
        'negotiation': 2,
        'booked': 3,
        'canceled': 4,
        'pending': 1,  // Map to in_progress
        'confirmed': 3 // Map to booked
    };
    
    return statusMap[status] || 0;
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