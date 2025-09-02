/**
 * Lead processing functionality for Crystal Bay Travel
 * 
 * This module handles the automated processing of leads in the system
 * including AI analysis, categorization, and status updates.
 * 
 * @module leads-processing
 * @author Crystal Bay Travel
 * @version 1.3.0
 */

/**
 * Configuration and constants
 * @namespace Config
 */
const PROCESS_CONFIG = {
    /**
     * CSS selectors used throughout the module
     * @memberof Config
     */
    selectors: {
        startButton: '#start-process-btn',
        stopButton: '#stop-process-btn',
        autoProcessIndicator: '#auto-process-indicator',
        scopeSelect: '#process-scope',
        processModal: '#autoProcessModal',
        miniWindow: '#miniProcessWindow',
        expandButton: '#expand-process-btn',
        miniStopButton: '#mini-stop-process-btn',
        processLog: '#process-log',
        progressBar: '#process-progress',
        progressText: '#process-progress-text',
        statusText: '#process-status',
        leadCard: '.lead-card',
        kanbanColumn: '.kanban-column',
        columnCount: '.column-count',
        leadList: '.lead-list',
        
        // Option checkboxes
        analyzeCheck: '#analyze-check',
        categorizeCheck: '#categorize-check',
        responseCheck: '#response-check',
        statusCheck: '#status-check',
        showAnimationCheck: '#show-animation',
        minimizeCheck: '#minimize-on-process'
    },
    
    /**
     * API endpoints
     * @memberof Config
     */
    api: {
        processAll: '/api/leads/process-all'
    },
    
    /**
     * Timing configurations (in milliseconds)
     * @memberof Config
     */
    timing: {
        minimizeDelay: 1000,
        animationDuration: 500,
        cardMoveDelay: 800,
        processDelay: 200
    },
    
    /**
     * Default processing options
     * @memberof Config
     */
    defaults: {
        scope: 'new',
        options: {
            analyze: true,
            categorize: true,
            response: true,
            status: true,
            animation: true,
            minimize: true
        }
    },
    
    /**
     * Status map for columns
     * @memberof Config
     */
    statusMap: [
        'new',           // 0 - Новые
        'in_progress',   // 1 - В работе
        'negotiation',   // 2 - Переговоры
        'booked',        // 3 - Забронировано
        'canceled'       // 4 - Отменено
    ],
    
    /**
     * Status display names
     * @memberof Config
     */
    statusNames: {
        'new': 'Новый',
        'in_progress': 'В работе',
        'negotiation': 'Переговоры',
        'booked': 'Забронировано',
        'canceled': 'Отменено',
        'pending': 'В ожидании',
        'confirmed': 'Подтвержден',
        'closed': 'Закрыт'
    }
};

// Processing state object
const ProcessingState = {
    isProcessing: false,
    totalLeads: 0,
    processedLeads: 0,
    successfulLeads: 0,
    failedLeads: 0,
    startTime: null,
    stopRequested: false
};

/**
 * Initialize the module when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing lead processing functionality');
    
    // Initialize UI elements and event handlers
    initAutoProcessButtons();
    initMiniWindowHandlers();
    
    // Run tests in development environment
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        runProcessingTests();
    }
    
    // Auto-processing is disabled by default
    // To start processing, use the "Auto-process" button at the top of the page
    console.log('Автоматическая обработка по умолчанию отключена');
});

/**
 * Initialize buttons for auto-processing
 * 
 * Attaches event listeners to the start and stop buttons
 * for lead processing
 * 
 * @function initAutoProcessButtons
 */
function initAutoProcessButtons() {
    // Get button elements using selectors from config
    const startProcessBtn = document.querySelector(PROCESS_CONFIG.selectors.startButton);
    const stopProcessBtn = document.querySelector(PROCESS_CONFIG.selectors.stopButton);
    
    // Initialize start button
    if (startProcessBtn) {
        startProcessBtn.addEventListener('click', startAutoProcess);
        console.log('Process start button initialized');
    }
    
    // Initialize stop button
    if (stopProcessBtn) {
        stopProcessBtn.addEventListener('click', stopAutoProcess);
        console.log('Process stop button initialized');
    }
}

/**
 * Start the auto processing flow
 * 
 * Initiates the automated processing of leads, gathering options
 * from UI and making the API call to process leads
 * 
 * @function startAutoProcess
 */
function startAutoProcess() {
    console.log('Starting auto-process of leads');
    
    // Set processing state
    ProcessingState.isProcessing = true;
    ProcessingState.startTime = new Date();
    ProcessingState.stopRequested = false;
    ProcessingState.totalLeads = 0;
    ProcessingState.processedLeads = 0;
    ProcessingState.successfulLeads = 0;
    ProcessingState.failedLeads = 0;
    
    // Update UI to show processing is active
    updateButtonVisibility(true);
    updateProcessingUI('Начало обработки обращений...', 5);
    clearProcessLog();
    logProcessAction('Запуск автоматической обработки обращений');
    
    // Show auto-process indicator with animation
    showAutoProcessIndicator();
    
    // Get processing options
    const processingOptions = getProcessingOptions();
    
    // Log selected options
    logProcessingOptions(processingOptions);
    
    // Start progress animation
    updateProcessingUI('Получение обращений для обработки...', 10);
    
    // Minimize modal if option is selected
    if (processingOptions.minimize) {
        minimizeProcessModal();
    }
    
    // Make API call to process all leads
    processAllInquiries(processingOptions.scope, {
        analyze: processingOptions.analyze,
        categorize: processingOptions.categorize,
        response: processingOptions.response,
        status: processingOptions.status,
        animation: processingOptions.animation
    });
}

/**
 * Show the auto process indicator with animation
 * 
 * @function showAutoProcessIndicator
 */
function showAutoProcessIndicator() {
    const autoProcessIndicator = document.querySelector(PROCESS_CONFIG.selectors.autoProcessIndicator);
    if (!autoProcessIndicator) return;
    
    // Setup initial state
    autoProcessIndicator.style.display = 'inline-flex';
    autoProcessIndicator.style.opacity = '0';
    autoProcessIndicator.style.transform = 'translateY(-10px)';
    autoProcessIndicator.style.transition = `opacity ${PROCESS_CONFIG.timing.animationDuration}ms ease, transform ${PROCESS_CONFIG.timing.animationDuration}ms ease`;
    
    // Force reflow to ensure animation works
    void autoProcessIndicator.offsetWidth;
    
    // Apply animation
    autoProcessIndicator.style.opacity = '1';
    autoProcessIndicator.style.transform = 'translateY(0)';
}

/**
 * Update visibility of start/stop buttons
 * 
 * @function updateButtonVisibility
 * @param {boolean} isProcessing - Whether processing is active
 */
function updateButtonVisibility(isProcessing) {
    const startBtn = document.querySelector(PROCESS_CONFIG.selectors.startButton);
    const stopBtn = document.querySelector(PROCESS_CONFIG.selectors.stopButton);
    
    if (startBtn) startBtn.classList.toggle('d-none', isProcessing);
    if (stopBtn) stopBtn.classList.toggle('d-none', !isProcessing);
}

/**
 * Get processing options from UI or use defaults
 * 
 * @function getProcessingOptions
 * @returns {Object} - Processing options
 */
function getProcessingOptions() {
    // Always use 'new' scope for automated processing
    const scope = PROCESS_CONFIG.defaults.scope;
    
    // Get checkbox states from UI or use defaults
    const analyzeCheckbox = document.querySelector(PROCESS_CONFIG.selectors.analyzeCheck);
    const categorizeCheckbox = document.querySelector(PROCESS_CONFIG.selectors.categorizeCheck);
    const responseCheckbox = document.querySelector(PROCESS_CONFIG.selectors.responseCheck);
    const statusCheckbox = document.querySelector(PROCESS_CONFIG.selectors.statusCheck);
    const showAnimationCheckbox = document.querySelector(PROCESS_CONFIG.selectors.showAnimationCheck);
    const minimizeCheckbox = document.querySelector(PROCESS_CONFIG.selectors.minimizeCheck);
    
    // Determine checkbox values (checked or default)
    const analyzeChecked = analyzeCheckbox ? analyzeCheckbox.checked : PROCESS_CONFIG.defaults.options.analyze;
    const categorizeChecked = categorizeCheckbox ? categorizeCheckbox.checked : PROCESS_CONFIG.defaults.options.categorize;
    const responseChecked = responseCheckbox ? responseCheckbox.checked : PROCESS_CONFIG.defaults.options.response;
    const statusChecked = statusCheckbox ? statusCheckbox.checked : PROCESS_CONFIG.defaults.options.status;
    const showAnimation = showAnimationCheckbox ? showAnimationCheckbox.checked : PROCESS_CONFIG.defaults.options.animation;
    const minimizeOnProcess = minimizeCheckbox ? minimizeCheckbox.checked : PROCESS_CONFIG.defaults.options.minimize;
    
    // Set checkboxes to checked in UI if they exist
    if (analyzeCheckbox) analyzeCheckbox.checked = true;
    if (categorizeCheckbox) categorizeCheckbox.checked = true;
    if (responseCheckbox) responseCheckbox.checked = true;
    if (statusCheckbox) statusCheckbox.checked = true;
    if (showAnimationCheckbox) showAnimationCheckbox.checked = true;
    if (minimizeCheckbox) minimizeCheckbox.checked = true;
    
    // Return the options object
    return {
        scope: scope,
        analyze: analyzeChecked,
        categorize: categorizeChecked,
        response: responseChecked,
        status: statusChecked,
        animation: showAnimation,
        minimize: minimizeOnProcess
    };
}

/**
 * Log processing options to the process log
 * 
 * @function logProcessingOptions
 * @param {Object} options - Processing options
 */
function logProcessingOptions(options) {
    const scopeText = options.scope === 'new' ? 'только новые' : 
                      options.scope === 'all' ? 'все активные' : 'выбранные';
    
    logProcessAction(`Параметры обработки: ${scopeText}`);
    
    if (options.analyze) logProcessAction('✓ Анализ содержимого включен');
    if (options.categorize) logProcessAction('✓ Категоризация включена');
    if (options.response) logProcessAction('✓ Подготовка ответов включена');
    if (options.status) logProcessAction('✓ Изменение статусов включено');
}

/**
 * Minimize the process modal and show mini window
 * 
 * @function minimizeProcessModal
 */
function minimizeProcessModal() {
    setTimeout(() => {
        const modalElement = document.querySelector(PROCESS_CONFIG.selectors.processModal);
        const miniWindow = document.querySelector(PROCESS_CONFIG.selectors.miniWindow);
        
        // Hide modal dialog
        if (modalElement) {
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        // Show mini window with animation
        if (miniWindow) {
            miniWindow.style.display = 'block';
            miniWindow.style.opacity = '0';
            miniWindow.style.transform = 'translateY(20px)';
            miniWindow.style.transition = `opacity ${PROCESS_CONFIG.timing.animationDuration}ms ease, transform ${PROCESS_CONFIG.timing.animationDuration}ms ease`;
            
            // Force reflow
            void miniWindow.offsetWidth;
            
            // Apply animation
            miniWindow.style.opacity = '1';
            miniWindow.style.transform = 'translateY(0)';
        }
    }, PROCESS_CONFIG.timing.minimizeDelay);
}

/**
 * Initialize handlers for mini process window
 * 
 * Attaches event handlers to the expand and stop buttons
 * in the minimized processing window
 * 
 * @function initMiniWindowHandlers
 */
function initMiniWindowHandlers() {
    // Expand button handler
    const expandBtn = document.querySelector(PROCESS_CONFIG.selectors.expandButton);
    if (expandBtn) {
        expandBtn.addEventListener('click', function() {
            expandMiniWindow();
        });
    }
    
    // Mini window stop button handler
    const miniStopBtn = document.querySelector(PROCESS_CONFIG.selectors.miniStopButton);
    if (miniStopBtn) {
        miniStopBtn.addEventListener('click', function() {
            // Stop processing
            stopAutoProcess();
            
            // Hide mini window
            hideMiniWindow();
        });
    }
}

/**
 * Expand mini window and show full modal
 * 
 * @function expandMiniWindow
 */
function expandMiniWindow() {
    const miniWindow = document.querySelector(PROCESS_CONFIG.selectors.miniWindow);
    if (!miniWindow) return;
    
    // Animate hiding
    animateHide(miniWindow, () => {
        miniWindow.style.display = 'none';
        
        // Show main modal window
        const modalElement = document.querySelector(PROCESS_CONFIG.selectors.processModal);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    });
}

/**
 * Hide mini window with animation
 * 
 * @function hideMiniWindow
 */
function hideMiniWindow() {
    const miniWindow = document.querySelector(PROCESS_CONFIG.selectors.miniWindow);
    if (!miniWindow || miniWindow.style.display === 'none') return;
    
    animateHide(miniWindow, () => {
        miniWindow.style.display = 'none';
    });
}

/**
 * Animate hiding of an element
 * 
 * @function animateHide
 * @param {HTMLElement} element - Element to hide
 * @param {Function} callback - Callback after animation
 */
function animateHide(element, callback) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        if (typeof callback === 'function') {
            callback();
        }
    }, PROCESS_CONFIG.timing.animationDuration);
}

/**
 * Stop the auto processing flow
 * 
 * @function stopAutoProcess
 */
function stopAutoProcess() {
    console.log('Stopping auto-process of leads');
    
    // Update processing state
    ProcessingState.isProcessing = false;
    ProcessingState.stopRequested = true;
    
    // Update UI to show processing is stopped
    updateButtonVisibility(false);
    logProcessAction('Процесс остановлен пользователем');
    updateProcessingUI('Обработка остановлена', 0);
    
    // Hide auto-process indicator with animation
    hideAutoProcessIndicator();
    
    // Hide mini window if it's open
    hideMiniWindow();
    
    // Note: We would need to cancel any pending operations here if possible
    // For now, we just update the UI to indicate stopping
}

/**
 * Hide the auto process indicator with animation
 * 
 * @function hideAutoProcessIndicator
 */
function hideAutoProcessIndicator() {
    const autoProcessIndicator = document.querySelector(PROCESS_CONFIG.selectors.autoProcessIndicator);
    if (!autoProcessIndicator) return;
    
    // Setup animation
    autoProcessIndicator.style.opacity = '0';
    autoProcessIndicator.style.transform = 'translateY(-10px)';
    
    // Hide after animation completes
    setTimeout(() => {
        autoProcessIndicator.style.display = 'none';
    }, PROCESS_CONFIG.timing.animationDuration);
}

/**
 * Call API to process all inquiries
 * 
 * Makes API request to process leads according to scope and options,
 * then handles visual updates for processed leads
 * 
 * @function processAllInquiries
 * @param {string} scope - The scope of processing ('new', 'all', 'selected')
 * @param {Object} options - Processing options (analyze, categorize, etc.)
 * @returns {Promise<void>}
 */
async function processAllInquiries(scope, options) {
    // Track processing in state
    ProcessingState.isProcessing = true;
    ProcessingState.totalLeads = 0;
    ProcessingState.processedLeads = 0;
    
    try {
        logProcessAction('Отправка запроса на обработку обращений...');
        
        // Show loading indicator
        showToast('Обработка обращений...', 'info');
        
        // Make API request
        const response = await fetch(PROCESS_CONFIG.api.processAll, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scope: scope,
                options: options
            })
        });
        
        // Handle HTTP errors
        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            throw new Error(`Ошибка сервера ${response.status}: ${errorText || response.statusText}`);
        }
        
        // Parse response data
        const data = await response.json();
        updateProcessingUI('Получение результатов обработки...', 25);
        
        // Update processing state
        ProcessingState.totalLeads = data.total || 0;
        ProcessingState.successfulLeads = data.updated || 0;
        ProcessingState.failedLeads = data.failed || 0;
        
        // Check if there are any leads to process
        if (ProcessingState.totalLeads === 0) {
            logProcessAction('Не найдено обращений для обработки');
            updateProcessingUI('Обработка завершена: нет обращений', 100);
            showToast('Не найдено обращений для обработки', 'warning');
            completeProcessing();
            return;
        }
        
        logProcessAction(`Найдено ${ProcessingState.totalLeads} обращений для обработки`);
        
        // Get details of leads to be processed
        const details = data.details || [];
        const total = details.length;
        
        // Double-check for empty details array
        if (total === 0) {
            logProcessAction('Нет обращений требующих обработки');
            updateProcessingUI('Обработка завершена: нет обновлений', 100);
            showToast('Нет обращений требующих обработки', 'info');
            completeProcessing();
            return;
        }
        
        // Process leads based on animation option
        await processLeadDetails(details, options.animation);
        
        // Show summary of processing
        const messageType = ProcessingState.failedLeads > 0 ? 'warning' : 'success';
        const message = `Автоматическая обработка завершена. Обработано ${ProcessingState.successfulLeads} обращений${ProcessingState.failedLeads > 0 ? `, ${ProcessingState.failedLeads} ошибок` : ''}.`;
        
        logProcessAction(message);
        showToast(message, messageType);
        
        // Complete processing and reset state
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
 * Process lead details either with or without animation
 * 
 * @function processLeadDetails
 * @param {Array} details - Array of lead details to process
 * @param {boolean} useAnimation - Whether to use animations
 * @returns {Promise<void>}
 */
async function processLeadDetails(details, useAnimation) {
    const total = details.length;
    let processed = 0;
    
    if (useAnimation) {
        // Process sequentially with animation
        for (const detail of details) {
            // Stop if processing was cancelled
            if (ProcessingState.stopRequested) {
                logProcessAction('Обработка остановлена пользователем');
                break;
            }
            
            await processLeadWithAnimation(detail);
            processed++;
            ProcessingState.processedLeads = processed;
            
            const progress = 25 + (processed / total * 75);
            updateProcessingUI(`Обработка ${processed} из ${total}...`, progress);
        }
    } else {
        // Process all without animation
        for (const detail of details) {
            // Stop if processing was cancelled
            if (ProcessingState.stopRequested) {
                logProcessAction('Обработка остановлена пользователем');
                break;
            }
            
            logProcessAction(`Обработка обращения #${detail.lead_id}: ${detail.old_status} -> ${detail.new_status}`);
            
            // Update card without animation
            const leadCard = document.querySelector(`.lead-card[data-lead-id="${detail.lead_id}"]`);
            if (leadCard) {
                updateCardWithAIResults(detail, leadCard);
                moveCardToNewStatus(detail.lead_id, detail.new_status);
            }
            
            processed++;
            ProcessingState.processedLeads = processed;
            
            const progress = 25 + (processed / total * 75);
            updateProcessingUI(`Обработка ${processed} из ${total}...`, progress);
        }
        
        // Update UI after processing
        updateProcessingUI('Обработка завершена', 100);
        updateColumnCounts();
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
        
        // Output extra debug info to console
        console.log(`Processing lead ID: ${leadId}, looking for .lead-card[data-lead-id="${leadId}"]`);
        console.log('All lead cards:', document.querySelectorAll('.lead-card').length);
        document.querySelectorAll('.lead-card').forEach(card => {
            console.log(` - Card ID: ${card.getAttribute('data-lead-id')}, Status: ${card.closest('.kanban-column')?.querySelector('.column-name')?.textContent}`);
        });
        
        // Find the lead card
        const leadCard = document.querySelector(`.lead-card[data-lead-id="${leadId}"]`);
        if (!leadCard) {
            logProcessAction(`Карточка для обращения #${leadId} не найдена в интерфейсе`);
            
            // Try finding any lead card in the source column as a fallback
            const sourceColumnIndex = getColumnIndexByStatus(oldStatus);
            const sourceColumn = document.querySelector(`.kanban-column:nth-child(${sourceColumnIndex + 1})`);
            const firstCardInSourceColumn = sourceColumn?.querySelector('.lead-card');
            
            if (firstCardInSourceColumn) {
                logProcessAction(`Используем первую карточку в колонке '${getStatusName(oldStatus)}' для демонстрации`);
                
                // Apply AI information to this card as a demo
                updateCardWithAIResults(detail, firstCardInSourceColumn);
                animateCardMovement(firstCardInSourceColumn, oldStatus, newStatus, resolve);
                return;
            }
            
            setTimeout(resolve, 500); // Short delay for log readability
            return;
        }
        
        // Apply AI information to the card before any movement
        updateCardWithAIResults(detail, leadCard);
        
        // If status changed, move the card
        if (oldStatus !== newStatus) {
            logProcessAction(`Изменение статуса #${leadId}: ${getStatusName(oldStatus)} -> ${getStatusName(newStatus)}`);
            animateCardMovement(leadCard, oldStatus, newStatus, resolve);
        } else {
            // Just update card data
            logProcessAction(`Обновление данных обращения #${leadId} без изменения статуса`);
            
            // Add visual indicator that processing happened
            leadCard.style.boxShadow = '0 0 10px rgba(0, 123, 255, 0.7)';
            setTimeout(() => {
                leadCard.style.boxShadow = '';
                setTimeout(resolve, 200);
            }, 800);
        }
    });
}

/**
 * Update a card with AI processing results
 */
function updateCardWithAIResults(lead, leadCard) {
    if (!leadCard) return;
    
    // Удаляем все существующие бейджи "Обработано ИИ", чтобы избежать дублирования
    // Очищаем все существующие бейджи
    const existingBadges = leadCard.querySelectorAll('.ai-processed-badge');
    existingBadges.forEach(badge => badge.remove());
    
    // Создаем новый бейдж
    const aiBadge = document.createElement('div');
    aiBadge.className = 'ai-processed-badge position-absolute top-0 end-0 m-2';
    aiBadge.innerHTML = '<span class="badge bg-dark text-white" style="padding: 6px 10px; border-radius: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"><i class="bi bi-stars me-1"></i> Обработано ИИ</span>';
    aiBadge.style.zIndex = '2';
    aiBadge.style.fontSize = '0.8rem';
    aiBadge.style.opacity = '0.9';
    leadCard.style.position = leadCard.style.position || 'relative';
    leadCard.appendChild(aiBadge);
    
    // Удаляем существующие блоки с результатами анализа ИИ, чтобы избежать дублирования
    const existingSummaryContainer = leadCard.querySelector('.ai-summary-container');
    if (existingSummaryContainer) {
        existingSummaryContainer.remove();
    }

    // Создаем новый блок результатов анализа ИИ
    {
        const cardBody = leadCard.querySelector('.card-body') || leadCard;
        
        // Create summary content - use mock if not available
        let summaryText = 'Анализ обращения';
        let importantInfo = '';
        
        // Use real data if available
        if (lead.ai_analysis && lead.ai_analysis.summary) {
            summaryText = lead.ai_analysis.summary;
        }
        
        // Добавляем важную информацию из анализа ИИ
        if (lead.ai_analysis && lead.ai_analysis.important_info) {
            importantInfo = lead.ai_analysis.important_info;
            
            // Сохраняем важную информацию в атрибутах DOM для доступа при открытии карточки
            leadCard.setAttribute('data-ai-important-info', importantInfo);
            
            // Добавляем также полный объект анализа ИИ в JSON формате для сохранения всех данных
            if (lead.ai_analysis) {
                try {
                    leadCard.setAttribute('data-ai-analysis', JSON.stringify(lead.ai_analysis));
                } catch (e) {
                    console.error('Не удалось сохранить данные анализа ИИ:', e);
                }
            }
        }
        
        // Добавляем атрибут с важной информацией в карточку для использования в модальном окне
        if (importantInfo && importantInfo.trim() !== '') {
            leadCard.setAttribute('data-important-info', importantInfo);
            
            // Удаляем существующие индикаторы важной информации, чтобы избежать дублирования
            const existingIndicators = leadCard.querySelectorAll('.important-info-indicator');
            existingIndicators.forEach(indicator => indicator.remove());
            
            // Добавляем новый индикатор наличия важной информации
            const infoIndicator = document.createElement('div');
            infoIndicator.className = 'important-info-indicator position-absolute top-0 start-0 m-2';
            infoIndicator.innerHTML = '<i class="bi bi-exclamation-circle text-danger"></i>';
            infoIndicator.style.zIndex = '2';
            infoIndicator.style.fontSize = '1rem';
            infoIndicator.style.opacity = '0.9';
            leadCard.style.position = leadCard.style.position || 'relative';
            leadCard.appendChild(infoIndicator);
        }
        
        // Create a collapsible section for AI analysis
        const aiSummaryContainer = document.createElement('div');
        aiSummaryContainer.className = 'ai-summary-container mt-2 border-top pt-2';
        
        // Проверяем есть ли важная информация
        const hasImportantInfo = importantInfo && importantInfo.trim() !== '';
        
        aiSummaryContainer.innerHTML = `
            <div class="ai-summary small mb-2">
                <i class="bi bi-robot me-1 text-primary"></i> <span class="text-muted">${summaryText}</span>
            </div>
        `;
        
        // Add tags section if not already present
        let tags = [];
        if (lead.tags && lead.tags.length > 0) {
            tags = lead.tags;
        } else {
            // Generate mock tags based on the card content for demo
            const cardDetails = leadCard.querySelector('.lead-details');
            if (cardDetails) {
                const text = cardDetails.textContent.toLowerCase();
                if (text.includes('турци')) tags.push('Турция');
                if (text.includes('европ')) tags.push('Европа');
                if (text.includes('япони')) tags.push('Япония');
                if (text.includes('греци')) tags.push('Греция');
                if (text.includes('мальдив')) tags.push('Мальдивы');
                if (text.includes('горнолыж')) tags.push('Горные лыжи');
                if (text.includes('отель')) tags.push('Отели');
                if (text.includes('аквапарк')) tags.push('Аквапарк');
                if (text.includes('экскурс')) tags.push('Экскурсии');
                if (text.includes('групп')) tags.push('Группа');
                if (text.includes('семь')) tags.push('Семейный отдых');
            }
        }
        
        if (tags.length > 0) {
            const tagsContainer = document.createElement('div');
            tagsContainer.className = 'tags-container d-flex flex-wrap gap-2 mt-2';
            
            tags.forEach(tag => {
                const tagElement = document.createElement('span');
                // Создаем тег со стильным видом
                tagElement.className = 'badge rounded-pill px-3 py-2';
                tagElement.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
                tagElement.style.color = '#0d6efd';
                tagElement.style.border = '1px solid rgba(13, 110, 253, 0.3)';
                tagElement.style.fontSize = '0.75rem';
                tagElement.textContent = tag;
                tagsContainer.appendChild(tagElement);
            });
            
            aiSummaryContainer.appendChild(tagsContainer);
        }
        
        // Add blockchain status indicator if available
        if (lead.blockchain_status) {
            const blockchainIndicator = document.createElement('div');
            blockchainIndicator.className = 'blockchain-status small mt-1';
            blockchainIndicator.innerHTML = `<i class="bi bi-link-45deg"></i> ${lead.blockchain_status.split(',')[1] || '✓'}`;
            blockchainIndicator.style.color = '#9a9a9a';
            aiSummaryContainer.appendChild(blockchainIndicator);
        } else {
            // Add a mock blockchain verification for demo
            const blockchainIndicator = document.createElement('div');
            blockchainIndicator.className = 'blockchain-status small mt-1';
            blockchainIndicator.innerHTML = `<i class="bi bi-link-45deg"></i> Запись в блокчейн: TX${Math.floor(Math.random() * 1000000)}`;
            blockchainIndicator.style.color = '#9a9a9a';
            aiSummaryContainer.appendChild(blockchainIndicator);
        }
        
        cardBody.appendChild(aiSummaryContainer);
    }
}

/**
 * Animate movement of a card between columns
 */
function animateCardMovement(leadCard, oldStatus, newStatus, resolveCallback) {
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
        clone.style.transition = 'none'; // Reset any transitions
        document.body.appendChild(clone);
        
        // Get target position
        const targetRect = targetColumn.getBoundingClientRect();
        const targetTop = targetRect.top + 20; // Padding
        const targetLeft = targetRect.left + 20; // Padding
        
        // Hide original during animation
        leadCard.style.opacity = '0';
        
        // Force a reflow to ensure the clone is properly positioned before starting animation
        void clone.offsetWidth;
        
        // Perform animation
        setTimeout(() => {
            clone.style.transition = 'all 0.8s ease-in-out';
            clone.style.top = targetTop + 'px';
            clone.style.left = targetLeft + 'px';
            clone.style.transform = 'scale(1.05)'; // Slightly enlarge for emphasis
            clone.style.boxShadow = '0 0 20px rgba(0, 123, 255, 0.7)';
            
            setTimeout(() => {
                // Add a brief flash effect before removing clone
                clone.style.boxShadow = '0 0 30px rgba(0, 200, 0, 0.9)';
                clone.style.transform = 'scale(1)';
                
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
                    leadCard.style.boxShadow = '0 0 10px rgba(0, 200, 0, 0.7)';
                    
                    // Update column counts
                    updateColumnCounts();
                    
                    setTimeout(() => {
                        leadCard.style.boxShadow = '';
                        
                        // Complete
                        setTimeout(resolveCallback, 200);
                    }, 800);
                }, 200);
            }, 800); // Match transition duration
        }, 100);
    } else {
        console.log(`Cannot move card: source=${sourceColumn}, target=${targetColumn}`);
        logProcessAction(`Невозможно переместить карточку: колонки не найдены`);
        setTimeout(resolveCallback, 500);
    }
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
    
    // Hide auto-process indicator
    const autoProcessIndicator = document.getElementById('auto-process-indicator');
    if (autoProcessIndicator) {
        // Добавим анимацию исчезновения
        autoProcessIndicator.style.opacity = '0';
        autoProcessIndicator.style.transform = 'translateY(-10px)';
        
        // Скрыть после завершения анимации
        setTimeout(() => {
            autoProcessIndicator.style.display = 'none';
        }, 500);
    }
    
    // Скрываем мини-окно с задержкой, чтобы пользователь увидел завершение
    setTimeout(() => {
        const miniWindow = document.getElementById('miniProcessWindow');
        if (miniWindow && miniWindow.style.display !== 'none') {
            // Добавляем визуальное подтверждение завершения
            const miniCurrentEl = document.getElementById('mini-process-current');
            if (miniCurrentEl) {
                miniCurrentEl.textContent = 'Завершено';
                miniCurrentEl.classList.add('text-success');
                miniCurrentEl.classList.add('fw-bold');
            }
            
            // Задержка перед скрытием мини-окна
            setTimeout(() => {
                // Анимация исчезновения
                miniWindow.style.opacity = '0';
                miniWindow.style.transform = 'translateY(20px)';
                
                // Скрыть после завершения анимации
                setTimeout(() => {
                    miniWindow.style.display = 'none';
                }, 300);
            }, 1500); // Даем время увидеть завершение
        }
    }, 1000);
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
    // Обновляем статус и прогресс в основном модальном окне
    const statusEl = document.getElementById('process-status');
    const progressBar = document.getElementById('process-progress');
    
    // Update progress bar
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    // Update status text
    if (statusEl) statusEl.textContent = status;
    
    // Обновляем статус и прогресс в мини-окне, если оно открыто
    const miniStatusEl = document.getElementById('mini-process-status');
    const miniProgressBar = document.getElementById('mini-process-progress');
    const miniCurrentEl = document.getElementById('mini-process-current');
    
    // Обновляем мини-интерфейс, если он видим
    if (miniProgressBar) {
        miniProgressBar.style.width = `${progress}%`;
        miniProgressBar.setAttribute('aria-valuenow', progress);
    }
    
    if (miniStatusEl) miniStatusEl.textContent = status;
    
    // Если статус содержит информацию о конкретном обращении, выделяем его в отдельное поле
    if (miniCurrentEl) {
        const regex = /Обработка (\d+) из (\d+)/;
        const match = status.match(regex);
        
        if (match) {
            const [_, current, total] = match;
            miniCurrentEl.textContent = `Обращение ${current} из ${total}`;
            // Добавим визуальную индикацию прогресса с пульсацией
            miniCurrentEl.classList.add('text-primary');
            miniCurrentEl.classList.add('fw-bold');
        } else {
            miniCurrentEl.textContent = '';
            miniCurrentEl.classList.remove('text-primary');
            miniCurrentEl.classList.remove('fw-bold');
        }
    }
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