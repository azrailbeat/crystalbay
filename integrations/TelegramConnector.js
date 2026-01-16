const BaseConnector = require('./BaseConnector');
const axios = require('axios');
const crypto = require('crypto');

class TelegramConnector extends BaseConnector {
    constructor() {
        super('telegram');
        this.botToken = null;
        this.webhookUrl = null;
        this.apiBase = 'https://api.telegram.org/bot';
    }

    async initialize(config) {
        this.config = config;
        this.botToken = config.bot_token || process.env.TELEGRAM_BOT_TOKEN;
        this.webhookUrl = config.webhook_url || null;

        if (!this.botToken) {
            console.warn('TelegramConnector: Bot token not configured');
            return false;
        }

        return true;
    }

    async connect() {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const response = await axios.get(`${this.apiBase}${this.botToken}/getMe`);
            if (response.data.ok) {
                this.isConnected = true;
                this.botInfo = response.data.result;
                console.log(`TelegramConnector: Connected as @${this.botInfo.username}`);
                return {
                    success: true,
                    bot_info: this.botInfo
                };
            }
        } catch (error) {
            console.error('TelegramConnector: Connection failed:', error.message);
            this.isConnected = false;
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

    async setWebhook(url) {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const response = await axios.post(`${this.apiBase}${this.botToken}/setWebhook`, {
                url: url,
                allowed_updates: ['message', 'callback_query', 'inline_query']
            });

            if (response.data.ok) {
                this.webhookUrl = url;
                return { success: true, message: 'Webhook set successfully' };
            }
            return { success: false, error: response.data.description };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async deleteWebhook() {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const response = await axios.post(`${this.apiBase}${this.botToken}/deleteWebhook`);
            if (response.data.ok) {
                this.webhookUrl = null;
                return { success: true };
            }
            return { success: false, error: response.data.description };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async sendMessage(chatId, message, options = {}) {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const payload = {
                chat_id: chatId,
                text: message,
                parse_mode: options.parse_mode || 'HTML'
            };

            if (options.reply_markup) {
                payload.reply_markup = options.reply_markup;
            }

            if (options.reply_to_message_id) {
                payload.reply_to_message_id = options.reply_to_message_id;
            }

            const response = await axios.post(`${this.apiBase}${this.botToken}/sendMessage`, payload);

            if (response.data.ok) {
                return {
                    success: true,
                    message_id: response.data.result.message_id,
                    external_message_id: String(response.data.result.message_id),
                    raw_response: response.data.result
                };
            }
            return { success: false, error: response.data.description };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async sendPhoto(chatId, photoUrl, caption = '', options = {}) {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const payload = {
                chat_id: chatId,
                photo: photoUrl,
                caption: caption,
                parse_mode: options.parse_mode || 'HTML'
            };

            const response = await axios.post(`${this.apiBase}${this.botToken}/sendPhoto`, payload);

            if (response.data.ok) {
                return {
                    success: true,
                    message_id: response.data.result.message_id,
                    raw_response: response.data.result
                };
            }
            return { success: false, error: response.data.description };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async sendDocument(chatId, documentUrl, caption = '', options = {}) {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const payload = {
                chat_id: chatId,
                document: documentUrl,
                caption: caption,
                parse_mode: options.parse_mode || 'HTML'
            };

            const response = await axios.post(`${this.apiBase}${this.botToken}/sendDocument`, payload);

            if (response.data.ok) {
                return {
                    success: true,
                    message_id: response.data.result.message_id,
                    raw_response: response.data.result
                };
            }
            return { success: false, error: response.data.description };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async getUpdates(offset = 0, limit = 100) {
        if (!this.botToken) {
            throw new Error('Telegram bot token not configured');
        }

        try {
            const response = await axios.get(`${this.apiBase}${this.botToken}/getUpdates`, {
                params: { offset, limit, timeout: 30 }
            });

            if (response.data.ok) {
                return {
                    success: true,
                    updates: response.data.result.map(u => this.normalizeIncomingMessage(u))
                };
            }
            return { success: false, error: response.data.description };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async handleWebhook(payload, signature = null) {
        try {
            const normalizedMessage = this.normalizeIncomingMessage(payload);
            return {
                success: true,
                message: normalizedMessage,
                raw_payload: payload
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    normalizeIncomingMessage(update) {
        const message = update.message || update.edited_message || update.channel_post;

        if (!message) {
            return null;
        }

        const sender = message.from || {};
        const chat = message.chat || {};

        let messageType = 'text';
        let content = message.text || '';
        let mediaUrl = null;
        let mediaType = null;

        if (message.photo) {
            messageType = 'photo';
            const photo = message.photo[message.photo.length - 1];
            mediaUrl = photo.file_id;
            mediaType = 'image';
            content = message.caption || '';
        } else if (message.document) {
            messageType = 'document';
            mediaUrl = message.document.file_id;
            mediaType = message.document.mime_type;
            content = message.caption || '';
        } else if (message.voice) {
            messageType = 'voice';
            mediaUrl = message.voice.file_id;
            mediaType = 'audio/ogg';
        } else if (message.video) {
            messageType = 'video';
            mediaUrl = message.video.file_id;
            mediaType = 'video';
            content = message.caption || '';
        } else if (message.sticker) {
            messageType = 'sticker';
            mediaUrl = message.sticker.file_id;
            content = message.sticker.emoji || '🎨';
        } else if (message.location) {
            messageType = 'location';
            content = `📍 ${message.location.latitude}, ${message.location.longitude}`;
        } else if (message.contact) {
            messageType = 'contact';
            content = `👤 ${message.contact.first_name} ${message.contact.last_name || ''}: ${message.contact.phone_number}`;
        }

        return {
            external_message_id: String(message.message_id),
            external_chat_id: String(chat.id),
            channel: 'telegram',
            direction: 'in',
            sender_type: 'customer',
            sender_id: String(sender.id || ''),
            sender_name: `${sender.first_name || ''} ${sender.last_name || ''}`.trim() || sender.username || 'Unknown',
            sender_username: sender.username || null,
            message_type: messageType,
            content: content,
            media_url: mediaUrl,
            media_type: mediaType,
            chat_type: chat.type,
            chat_title: chat.title || null,
            metadata: {
                update_id: update.update_id,
                date: message.date,
                chat_id: chat.id,
                is_bot: sender.is_bot || false
            }
        };
    }

    getStatus() {
        return {
            channel: this.channelName,
            connected: this.isConnected,
            bot_token_set: !!this.botToken,
            webhook_url: this.webhookUrl,
            bot_info: this.botInfo || null
        };
    }
}

module.exports = new TelegramConnector();