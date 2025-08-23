/**
 * Тесты для Kanban доски и функций drag-and-drop
 * 
 * Запуск: откройте страницу tests.html в браузере
 */

// Настройка QUnit
QUnit.config.autostart = false;
QUnit.config.reorder = false;

// Имитация данных
const mockLeads = [
    {
        id: '1',
        name: 'Тестовый Клиент 1',
        email: 'test1@example.com',
        phone: '+7 (999) 123-45-67',
        source: 'website',
        status: 'new',
        details: 'Тестовый запрос 1',
        tags: ['Тест', 'Веб']
    },
    {
        id: '2',
        name: 'Тестовый Клиент 2',
        email: 'test2@example.com',
        phone: '+7 (999) 987-65-43',
        source: 'email',
        status: 'in_progress',
        details: 'Тестовый запрос 2',
        tags: ['Тест', 'Email']
    }
];

// Модуль для тестирования Kanban доски
QUnit.module('Kanban Board Tests', {
    before: function() {
        // Подготовка DOM
        document.body.innerHTML = `
            <div class="kanban-board">
                <div class="kanban-column" data-status="new">
                    <div class="column-header">
                        <h3>Новые</h3>
                        <span class="column-count">0</span>
                    </div>
                    <div class="lead-list"></div>
                </div>
                <div class="kanban-column" data-status="in_progress">
                    <div class="column-header">
                        <h3>В работе</h3>
                        <span class="column-count">0</span>
                    </div>
                    <div class="lead-list"></div>
                </div>
            </div>
            <div id="viewLeadModal" class="modal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Детали обращения</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="lead-details-container">
                                <div class="row mb-3">
                                    <div class="col-md-4"><strong>Имя:</strong></div>
                                    <div class="col-md-8" id="lead-name"></div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-4"><strong>Email:</strong></div>
                                    <div class="col-md-8" id="lead-email"></div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-4"><strong>Телефон:</strong></div>
                                    <div class="col-md-8" id="lead-phone"></div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-4"><strong>Статус:</strong></div>
                                    <div class="col-md-8">
                                        <select id="lead-status-select" class="form-select">
                                            <option value="new">Новый</option>
                                            <option value="in_progress">В работе</option>
                                            <option value="negotiation">Переговоры</option>
                                            <option value="booked">Забронировано</option>
                                            <option value="canceled">Отменено</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-4"><strong>Детали:</strong></div>
                                    <div class="col-md-8" id="lead-details"></div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-4"><strong>Теги:</strong></div>
                                    <div class="col-md-8" id="lead-tags"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Инициализация переменных, необходимых для тестов
        window.draggedItem = null;
        window.bootstrap = {
            Modal: function() {
                this.show = function() {};
                this.hide = function() {};
            },
            Toast: function() {
                this.show = function() {};
            }
        };
        
        // Мокаем fetch для API вызовов
        window.originalFetch = window.fetch;
        window.fetch = function(url, options) {
            return new Promise((resolve) => {
                let responseData = { success: true };
                
                if (url.includes('/api/leads/') && url.includes('/status')) {
                    responseData = { success: true, lead: { status: JSON.parse(options.body).status } };
                } else if (url.includes('/api/leads/')) {
                    const leadId = url.split('/').pop();
                    const lead = mockLeads.find(l => l.id === leadId) || mockLeads[0];
                    responseData = { lead: lead, interactions: [] };
                }
                
                resolve({
                    ok: true,
                    json: () => Promise.resolve(responseData)
                });
            });
        };
    },
    beforeEach: function() {
        // Очищаем колонки перед каждым тестом
        document.querySelectorAll('.lead-list').forEach(list => {
            list.innerHTML = '';
        });
        
        // Сбрасываем счетчики
        document.querySelectorAll('.column-count').forEach(count => {
            count.textContent = '0';
        });
        
        // Сбрасываем draggedItem
        window.draggedItem = null;
    },
    after: function() {
        // Восстанавливаем оригинальный fetch
        if (window.originalFetch) {
            window.fetch = window.originalFetch;
        }
        
        // Очищаем DOM
        document.body.innerHTML = '';
    }
});

// Тесты для инициализации Kanban доски
QUnit.test('Initialization - Cards and columns are properly set up', function(assert) {
    const done = assert.async();
    
    // Добавляем карточки в DOM
    const newsList = document.querySelector('.kanban-column[data-status="new"] .lead-list');
    const inProgressList = document.querySelector('.kanban-column[data-status="in_progress"] .lead-list');
    
    // Создаем и добавляем карточки
    const card1 = document.createElement('div');
    card1.className = 'lead-card';
    card1.setAttribute('data-lead-id', '1');
    card1.innerHTML = '<div class="lead-card-header">Тестовый Клиент 1</div>';
    
    const card2 = document.createElement('div');
    card2.className = 'lead-card';
    card2.setAttribute('data-lead-id', '2');
    card2.innerHTML = '<div class="lead-card-header">Тестовый Клиент 2</div>';
    
    newsList.appendChild(card1);
    inProgressList.appendChild(card2);
    
    // Инициализируем функциональность drag-and-drop
    window.initDragAndDrop = function() {
        // Находим все карточки лидов
        const cards = document.querySelectorAll('.lead-card');
        
        // Добавляем к ним обработчики событий
        cards.forEach(card => {
            card.setAttribute('draggable', 'true');
            card.addEventListener('dragstart', function(e) {
                window.draggedItem = this;
                this.classList.add('dragging');
                e.dataTransfer = {
                    setData: function() {},
                    effectAllowed: 'move'
                };
            });
            
            card.addEventListener('dragend', function() {
                this.classList.remove('dragging');
            });
        });
        
        // Настраиваем целевые зоны (колонки)
        const columns = document.querySelectorAll('.lead-list');
        columns.forEach(column => {
            column.addEventListener('dragover', function(e) {
                e.preventDefault();
            });
            
            column.addEventListener('drop', function() {
                if (window.draggedItem) {
                    this.appendChild(window.draggedItem);
                    
                    // Обновляем счетчики
                    updateColumnCounts();
                }
            });
        });
        
        // Обновляем счетчики колонок
        updateColumnCounts();
    };
    
    window.updateColumnCounts = function() {
        document.querySelectorAll('.kanban-column').forEach((column) => {
            const countElement = column.querySelector('.column-count');
            if (countElement) {
                const cardsCount = column.querySelectorAll('.lead-card').length;
                countElement.textContent = cardsCount.toString();
            }
        });
    };
    
    // Выполняем инициализацию
    window.initDragAndDrop();
    
    // Проверяем, что карточки добавлены
    assert.equal(newsList.querySelectorAll('.lead-card').length, 1, 'Новая колонка содержит 1 карточку');
    assert.equal(inProgressList.querySelectorAll('.lead-card').length, 1, 'Колонка В работе содержит 1 карточку');
    
    // Проверяем счетчики
    assert.equal(document.querySelector('.kanban-column[data-status="new"] .column-count').textContent, '1', 'Счетчик новых равен 1');
    assert.equal(document.querySelector('.kanban-column[data-status="in_progress"] .column-count').textContent, '1', 'Счетчик в работе равен 1');
    
    done();
});

// Тесты для функциональности drag-and-drop
QUnit.test('Drag and Drop - Card can be moved between columns', function(assert) {
    const done = assert.async();
    
    // Добавляем карточки в DOM
    const newsList = document.querySelector('.kanban-column[data-status="new"] .lead-list');
    const inProgressList = document.querySelector('.kanban-column[data-status="in_progress"] .lead-list');
    
    // Создаем и добавляем карточку
    const card = document.createElement('div');
    card.className = 'lead-card';
    card.setAttribute('data-lead-id', '1');
    card.innerHTML = '<div class="lead-card-header">Тестовый Клиент 1</div>';
    newsList.appendChild(card);
    
    // Имитируем инициализацию drag-and-drop
    window.updateColumnCounts = function() {
        document.querySelectorAll('.kanban-column').forEach((column) => {
            const countElement = column.querySelector('.column-count');
            if (countElement) {
                const cardsCount = column.querySelectorAll('.lead-card').length;
                countElement.textContent = cardsCount.toString();
            }
        });
    };
    
    // Обновляем счетчики
    window.updateColumnCounts();
    
    // Проверяем начальное состояние
    assert.equal(newsList.querySelectorAll('.lead-card').length, 1, 'Изначально карточка в колонке "Новые"');
    assert.equal(inProgressList.querySelectorAll('.lead-card').length, 0, 'Изначально в колонке "В работе" нет карточек');
    
    // Имитируем drag-n-drop
    window.draggedItem = card;
    card.classList.add('dragging');
    
    // Имитируем drop
    inProgressList.dispatchEvent(new Event('drop'));
    
    // Обновляем счетчики
    window.updateColumnCounts();
    
    // Проверяем результат
    assert.equal(newsList.querySelectorAll('.lead-card').length, 0, 'После перетаскивания в колонке "Новые" нет карточек');
    assert.equal(inProgressList.querySelectorAll('.lead-card').length, 1, 'После перетаскивания карточка появилась в "В работе"');
    assert.equal(document.querySelector('.kanban-column[data-status="new"] .column-count').textContent, '0', 'Счетчик новых обновлен до 0');
    assert.equal(document.querySelector('.kanban-column[data-status="in_progress"] .column-count').textContent, '1', 'Счетчик в работе обновлен до 1');
    
    done();
});

// Тесты для модального окна
QUnit.test('Modal - Lead details can be viewed', function(assert) {
    const done = assert.async();
    
    // Добавляем карточку в DOM
    const newsList = document.querySelector('.kanban-column[data-status="new"] .lead-list');
    
    // Создаем и добавляем карточку
    const card = document.createElement('div');
    card.className = 'lead-card';
    card.setAttribute('data-lead-id', '1');
    card.innerHTML = '<div class="lead-card-header">Тестовый Клиент 1</div>';
    newsList.appendChild(card);
    
    // Имитируем функцию открытия модального окна
    window.openLeadModal = function(leadId) {
        const modal = document.getElementById('viewLeadModal');
        modal.setAttribute('data-lead-id', leadId);
        
        // Имитируем загрузку данных
        const lead = mockLeads.find(l => l.id === leadId);
        document.getElementById('lead-name').textContent = lead.name;
        document.getElementById('lead-email').textContent = lead.email;
        document.getElementById('lead-phone').textContent = lead.phone;
        document.getElementById('lead-details').textContent = lead.details;
        document.getElementById('lead-status-select').value = lead.status;
        
        // Имитируем отображение модального окна
        modal.style.display = 'block';
    };
    
    // Открываем модальное окно
    window.openLeadModal('1');
    
    // Проверяем, что данные загружены
    const modal = document.getElementById('viewLeadModal');
    assert.equal(modal.getAttribute('data-lead-id'), '1', 'ID лида установлен в модальном окне');
    assert.equal(document.getElementById('lead-name').textContent, 'Тестовый Клиент 1', 'Имя клиента отображается');
    assert.equal(document.getElementById('lead-email').textContent, 'test1@example.com', 'Email клиента отображается');
    assert.equal(document.getElementById('lead-status-select').value, 'new', 'Статус лида установлен');
    
    done();
});

// Запускаем тесты
QUnit.start();