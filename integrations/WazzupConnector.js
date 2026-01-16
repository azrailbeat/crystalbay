const BaseConnector = require('./BaseConnector');
const axios = require('axios');

class WazzupConnector extends BaseConnector {
    constructor() {
        super('wazzup');
        this.apiKey = null;
        this.apiBase = 'https://api.wazzup24.com/v3';
        this.channelId = null;
    }

    async initialize(config) {
        this.config = config;
        this.apiKey = config.api_key || process.env.WAZZUP_API_KEY;
        this.channelId = config.channel_id || process.env.WAZZUP_CHANNEL_ID;

        if (!this.apiKey) {
            console.warn('WazzupConnector: API key not configured');
            return false;
        }

        return true;
    }

    async connect() {
        if (!this.apiKey) {
            return {
                success: false,
                error: 'Wazzup API key not configured'
            };
        }

        try {
            const response = await axios.get(`${this.apiBase}/channels`, {
                headers: this.getHeaders(),
                timeout: 10000
            });

            if (response.status === 200) {
                this.isConnected = true;
                this.channels = response.data;
                console.log('WazzupConnector: Connected successfully');
                return {
                    success: true,
                    channels: this.channels
                };
            }
        } catch (error) {
            console.error('WazzupConnector: Connection failed:', error.message);
            this.isConnected = false;

            if (error.response) {
                return {
                    success: false,
                    error: `HTTP ${error.response.status}: ${error.response.statusText}`,
                    details: error.response.data
                };
            }
            return {
                success: false,
                error: error.message
            };
        }
    }

    async disconnect() {
        this.isConnected = false;
        return { success: true };
    }

    getHeaders() {
        return {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async getChannels() {
        if (!this.apiKey) {
            return { success: false, error: 'API key not configured' };
        }

        try {
            const response = await axios.get(`${this.apiBase}/channels`, {
                headers: this.getHeaders(),
                timeout: 10000
            });

            return {
                success: true,
                channels: response.data
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async sendMessage(chatId, message, options = {}) {
        if (!this.apiKey) {
            return { success: false, error: 'API key not configured' };
        }

        const channelId = options.channel_id || this.channelId;
        if (!channelId) {
            return { success: false, error: 'Channel ID not specified' };
        }

        try {
            const payload = {
                channelId: channelId,
                chatId: chatId,
                chatType: options.chat_type || 'whatsapp',
                text: message
            };

            const response = await axios.post(`${this.apiBase}/message`, payload, {
                headers: this.getHeaders(),
                timeout: 30000
            });

            if (response.status === 200 || response.status === 201) {
                return {
                    success: true,
                    message_id: response.data.messageId,
                    external_message_id: response.data.messageId,
                    raw_response: response.data
                };
            }
            return { success: false, error: 'Failed to send message' };
        } catch (error) {
            if (error.response) {
                return {
                    success: false,
                    error: `HTTP ${error.response.status}: ${error.response.statusText}`,
                    details: error.response.data
                };
            }
            return { success: false, error: error.message };
        }
    }

    async sendFile(chatId, fileUrl, fileName, options = {}) {
        if (!this.apiKey) {
            return { success: false, error: 'API key not configured' };
        }

        const channelId = options.channel_id || this.channelId;
        if (!channelId) {
            return { success: false, error: 'Channel ID not specified' };
        }

        try {
            const payload = {
                channelId: channelId,
                chatId: chatId,
                chatType: options.chat_type || 'whatsapp',
                contentUri: fileUrl,
                fileName: fileName
            };

            const response = await axios.post(`${this.apiBase}/message`, payload, {
                headers: this.getHeaders(),
                timeout: 30000
            });

            if (response.status === 200 || response.status === 201) {
                return {
                    success: true,
                    message_id: response.data.messageId,
                    raw_response: response.data
                };
            }
            return { success: false, error: 'Failed to send file' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async getContacts() {
        if (!this.apiKey) {
            return { success: false, error: 'API key not configured' };
        }

        try {
            const response = await axios.get(`${this.apiBase}/contacts`, {
                headers: this.getHeaders(),
                timeout: 10000
            });

            return {
                success: true,
                contacts: response.data
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async handleWebhook(payload, signature = null) {
        try {
            const messages = payload.messages || [];
            const normalizedMessages = messages.map(msg => this.normalizeIncomingMessage(msg));

            return {
                success: true,
                messages: normalizedMessages,
                raw_payload: payload
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    normalizeIncomingMessage(rawMessage) {
        const isIncoming = rawMessage.isIncome !== false;

        let messageType = 'text';
        let content = rawMessage.text || '';
        let mediaUrl = null;
        let mediaType = null;

        if (rawMessage.contentUri) {
            if (rawMessage.contentType) {
                if (rawMessage.contentType.startsWith('image/')) {
                    messageType = 'photo';
                    mediaType = 'image';
                } else if (rawMessage.contentType.startsWith('video/')) {
                    messageType = 'video';
                    mediaType = 'video';
                } else if (rawMessage.contentType.startsWith('audio/')) {
                    messageType = 'voice';
                    mediaType = 'audio';
                } else {
                    messageType = 'document';
                    mediaType = rawMessage.contentType;
                }
            }
            mediaUrl = rawMessage.contentUri;
            content = rawMessage.text || rawMessage.fileName || '';
        }

        return {
            external_message_id: rawMessage.messageId || rawMessage.id,
            external_chat_id: rawMessage.chatId,
            channel: rawMessage.chatType === 'telegram' ? 'telegram' : 'whatsapp',
            direction: isIncoming ? 'in' : 'out',
            sender_type: isIncoming ? 'customer' : 'agent',
            sender_id: rawMessage.chatId,
            sender_name: rawMessage.name || rawMessage.chatId,
            sender_phone: rawMessage.chatId,
            message_type: messageType,
            content: content,
            media_url: mediaUrl,
            media_type: mediaType,
            metadata: {
                channel_id: rawMessage.channelId,
                chat_type: rawMessage.chatType,
                timestamp: rawMessage.dateTime || rawMessage.time,
                status: rawMessage.status
            }
        };
    }

    getStatus() {
        return {
            channel: this.channelName,
            connected: this.isConnected,
            api_key_set: !!this.apiKey,
            channel_id: this.channelId,
            channels: this.channels || []
        };
    }
}

module.exports = new WazzupConnector();