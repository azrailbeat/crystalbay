/**
 * Wazzup24 Chat History Component for Crystal Bay Travel
 * Displays chat history from Wazzup24 in lead detail cards
 */

class WazzupChatWidget {
    constructor(containerId, leadId) {
        this.containerId = containerId;
        this.leadId = leadId;
        this.container = document.getElementById(containerId);
        this.chatHistory = [];
        this.channels = [];
        this.currentChannelId = null;
        this.contactId = null;
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }
        
        this.render();
        this.loadChatHistory();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="wazzup-chat-widget">
                <div class="chat-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <i class="bi bi-whatsapp text-success"></i>
                            История общения Wazzup24
                        </h6>
                        <div class="chat-controls">
                            <select class="form-select form-select-sm" id="channel-select-${this.leadId}" style="width: auto;">
                                <option value="">Все каналы</option>
                            </select>
                            <button class="btn btn-sm btn-outline-primary ms-2" onclick="this.refreshChat()" id="refresh-chat-${this.leadId}">
                                <i class="bi bi-arrow-clockwise"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="chat-messages" id="chat-messages-${this.leadId}">
                    <div class="loading-state text-center py-3">
                        <div class="spinner-border spinner-border-sm" role="status"></div>
                        <div class="ms-2">Загружаем историю чата...</div>
                    </div>
                </div>
                
                <div class="chat-input" id="chat-input-${this.leadId}" style="display: none;">
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="Введите сообщение..." id="message-input-${this.leadId}">
                        <button class="btn btn-primary" onclick="this.sendMessage()" id="send-btn-${this.leadId}">
                            <i class="bi bi-send"></i>
                        </button>
                    </div>
                </div>
                
                <style>
                    .wazzup-chat-widget {
                        border: 1px solid #dee2e6;
                        border-radius: 0.5rem;
                        background: white;
                        margin-bottom: 1rem;
                    }
                    
                    .chat-header {
                        padding: 0.75rem;
                        border-bottom: 1px solid #dee2e6;
                        background: #f8f9fa;
                        border-radius: 0.5rem 0.5rem 0 0;
                    }
                    
                    .chat-messages {
                        max-height: 400px;
                        overflow-y: auto;
                        padding: 0.75rem;
                    }
                    
                    .message-item {
                        margin-bottom: 0.75rem;
                        padding: 0.5rem;
                        border-radius: 0.5rem;
                        max-width: 80%;
                    }
                    
                    .message-incoming {
                        background: #e3f2fd;
                        margin-right: auto;
                        border-bottom-left-radius: 0.25rem;
                    }
                    
                    .message-outgoing {
                        background: #e8f5e8;
                        margin-left: auto;
                        border-bottom-right-radius: 0.25rem;
                    }
                    
                    .message-content {
                        margin-bottom: 0.25rem;
                        word-wrap: break-word;
                    }
                    
                    .message-meta {
                        font-size: 0.75rem;
                        color: #6c757d;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    
                    .channel-badge {
                        font-size: 0.6rem;
                        padding: 0.125rem 0.25rem;
                        border-radius: 0.25rem;
                    }
                    
                    .chat-input {
                        padding: 0.75rem;
                        border-top: 1px solid #dee2e6;
                    }
                    
                    .empty-state {
                        text-align: center;
                        padding: 2rem;
                        color: #6c757d;
                    }
                </style>
            </div>
        `;
        
        // Привязываем обработчики событий
        this.bindEvents();
    }
    
    bindEvents() {
        // Обновление чата
        const refreshBtn = document.getElementById(`refresh-chat-${this.leadId}`);
        if (refreshBtn) {
            refreshBtn.onclick = () => this.refreshChat();
        }
        
        // Переключение канала
        const channelSelect = document.getElementById(`channel-select-${this.leadId}`);
        if (channelSelect) {
            channelSelect.onchange = () => this.onChannelChange();
        }
        
        // Отправка сообщения
        const sendBtn = document.getElementById(`send-btn-${this.leadId}`);
        if (sendBtn) {
            sendBtn.onclick = () => this.sendMessage();
        }
        
        const messageInput = document.getElementById(`message-input-${this.leadId}`);
        if (messageInput) {
            messageInput.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            };
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`/api/leads/${this.leadId}/wazzup-chat`);
            const data = await response.json();
            
            if (data.success) {
                this.chatHistory = data.chat_history || [];
                this.channels = data.channels || [];
                this.contactId = data.contact_id;
                
                this.updateChannelSelect();
                this.renderMessages();
                
                // Показываем поле ввода если есть активные каналы
                if (this.channels.length > 0) {
                    const chatInput = document.getElementById(`chat-input-${this.leadId}`);
                    if (chatInput) chatInput.style.display = 'block';
                }
            } else {
                this.renderError(data.message || 'Ошибка загрузки чата');
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.renderError('Ошибка подключения к Wazzup24');
        }
    }
    
    updateChannelSelect() {
        const select = document.getElementById(`channel-select-${this.leadId}`);
        if (!select) return;
        
        // Очищаем текущие опции кроме "Все каналы"
        while (select.options.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Добавляем каналы
        this.channels.forEach(channel => {
            const option = document.createElement('option');
            option.value = channel.id;
            option.textContent = `${this.getChannelTypeLabel(channel.type)} - ${channel.name}`;
            select.appendChild(option);
        });
    }
    
    renderMessages() {
        const messagesContainer = document.getElementById(`chat-messages-${this.leadId}`);
        if (!messagesContainer) return;
        
        if (this.chatHistory.length === 0) {
            messagesContainer.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-chat-dots"></i>
                    <p>История сообщений пуста</p>
                    ${this.contactId ? '<small>Контакт найден в Wazzup24, но сообщений пока нет</small>' : '<small>Контакт не найден в Wazzup24</small>'}
                </div>
            `;
            return;
        }
        
        const filteredMessages = this.currentChannelId 
            ? this.chatHistory.filter(msg => msg.channel_id === this.currentChannelId)
            : this.chatHistory;
        
        const messagesHtml = filteredMessages.map(message => this.renderMessage(message)).join('');
        messagesContainer.innerHTML = messagesHtml;
        
        // Прокручиваем к последнему сообщению
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    renderMessage(message) {
        const isIncoming = message.direction === 'incoming';
        const messageClass = isIncoming ? 'message-incoming' : 'message-outgoing';
        const senderName = isIncoming ? message.sender_name : (message.operator_name || 'Оператор');
        
        return `
            <div class="message-item ${messageClass}">
                <div class="message-content">${this.escapeHtml(message.content)}</div>
                <div class="message-meta">
                    <span>${senderName}</span>
                    <span>
                        <span class="channel-badge bg-secondary text-white">
                            ${this.getChannelTypeLabel(message.channel)}
                        </span>
                        ${this.formatMessageTime(message.timestamp)}
                    </span>
                </div>
            </div>
        `;
    }
    
    renderError(message) {
        const messagesContainer = document.getElementById(`chat-messages-${this.leadId}`);
        if (!messagesContainer) return;
        
        messagesContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-exclamation-triangle text-warning"></i>
                <p>${message}</p>
            </div>
        `;
    }
    
    async sendMessage() {
        const messageInput = document.getElementById(`message-input-${this.leadId}`);
        const sendBtn = document.getElementById(`send-btn-${this.leadId}`);
        
        if (!messageInput || !sendBtn) return;
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        if (!this.currentChannelId && this.channels.length > 0) {
            alert('Выберите канал для отправки сообщения');
            return;
        }
        
        const channelId = this.currentChannelId || (this.channels.length > 0 ? this.channels[0].id : null);
        if (!channelId) {
            alert('Нет доступных каналов для отправки');
            return;
        }
        
        // Блокируем кнопку
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
        
        try {
            const response = await fetch(`/api/leads/${this.leadId}/wazzup-send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    channel_id: channelId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                messageInput.value = '';
                // Перезагружаем чат через 1 секунду для отображения отправленного сообщения
                setTimeout(() => this.refreshChat(), 1000);
            } else {
                alert(data.message || 'Ошибка отправки сообщения');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Ошибка отправки сообщения');
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="bi bi-send"></i>';
        }
    }
    
    onChannelChange() {
        const select = document.getElementById(`channel-select-${this.leadId}`);
        if (!select) return;
        
        this.currentChannelId = select.value || null;
        this.renderMessages();
    }
    
    refreshChat() {
        this.loadChatHistory();
    }
    
    getChannelTypeLabel(type) {
        const labels = {
            'whatsapp': 'WhatsApp',
            'telegram': 'Telegram',
            'vk': 'ВКонтакте',
            'instagram': 'Instagram',
            'viber': 'Viber'
        };
        return labels[type] || type;
    }
    
    formatMessageTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffHours < 1) return 'Сейчас';
        if (diffHours < 24) return `${diffHours} ч назад`;
        if (diffDays < 7) return `${diffDays} дн назад`;
        
        return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Глобальная функция для инициализации виджета
window.initWazzupChat = function(containerId, leadId) {
    return new WazzupChatWidget(containerId, leadId);
};