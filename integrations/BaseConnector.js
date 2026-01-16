class BaseConnector {
    constructor(channelName) {
        this.channelName = channelName;
        this.isConnected = false;
        this.config = {};
    }

    async initialize(config) {
        this.config = config;
        throw new Error('initialize() must be implemented by subclass');
    }

    async connect() {
        throw new Error('connect() must be implemented by subclass');
    }

    async disconnect() {
        throw new Error('disconnect() must be implemented by subclass');
    }

    async sendMessage(chatId, message, options = {}) {
        throw new Error('sendMessage() must be implemented by subclass');
    }

    async getMessages(chatId, options = {}) {
        throw new Error('getMessages() must be implemented by subclass');
    }

    async handleWebhook(payload, signature = null) {
        throw new Error('handleWebhook() must be implemented by subclass');
    }

    validateWebhook(payload, signature) {
        return true;
    }

    normalizeIncomingMessage(rawMessage) {
        return {
            external_message_id: null,
            channel: this.channelName,
            direction: 'in',
            sender_type: 'customer',
            sender_id: null,
            sender_name: 'Unknown',
            message_type: 'text',
            content: '',
            media_url: null,
            media_type: null,
            metadata: {}
        };
    }

    normalizeOutgoingMessage(message) {
        return message;
    }

    getStatus() {
        return {
            channel: this.channelName,
            connected: this.isConnected,
            config_set: Object.keys(this.config).length > 0
        };
    }
}

module.exports = BaseConnector;