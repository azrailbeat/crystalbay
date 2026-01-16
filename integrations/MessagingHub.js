const MessageService = require('../models/MessageService');
const TelegramConnector = require('./TelegramConnector');
const WazzupConnector = require('./WazzupConnector');

class MessagingHub {
    constructor() {
        this.connectors = {
            telegram: TelegramConnector,
            wazzup: WazzupConnector,
            whatsapp: WazzupConnector
        };
        this.messageService = MessageService;
        this.automationRules = [];
        this.isInitialized = false;
    }

    async initialize() {
        console.log('MessagingHub: Initializing connectors...');

        const results = {};

        if (process.env.TELEGRAM_BOT_TOKEN) {
            const telegramInit = await TelegramConnector.initialize({
                bot_token: process.env.TELEGRAM_BOT_TOKEN
            });
            if (telegramInit) {
                const connectResult = await TelegramConnector.connect();
                results.telegram = connectResult;
            }
        } else {
            results.telegram = { success: false, error: 'Bot token not configured' };
        }

        if (process.env.WAZZUP_API_KEY) {
            const wazzupInit = await WazzupConnector.initialize({
                api_key: process.env.WAZZUP_API_KEY,
                channel_id: process.env.WAZZUP_CHANNEL_ID
            });
            if (wazzupInit) {
                const connectResult = await WazzupConnector.connect();
                results.wazzup = connectResult;
            }
        } else {
            results.wazzup = { success: false, error: 'API key not configured' };
        }

        this.isInitialized = true;
        console.log('MessagingHub: Initialization complete');
        return results;
    }

    getConnector(channel) {
        const connector = this.connectors[channel.toLowerCase()];
        if (!connector) {
            throw new Error(`Unknown channel: ${channel}`);
        }
        return connector;
    }

    async sendMessage(channel, chatId, message, options = {}) {
        const connector = this.getConnector(channel);

        const result = await connector.sendMessage(chatId, message, options);

        if (result.success) {
            let conversation = await this.messageService.findConversation(channel, chatId);

            if (!conversation) {
                conversation = await this.messageService.createConversation({
                    channel,
                    external_chat_id: chatId,
                    participant_name: options.participant_name || 'Unknown',
                    participant_phone: options.participant_phone || null,
                    lead_id: options.lead_id || null
                });
            }

            await this.messageService.createMessage({
                conversation_id: conversation.id,
                channel,
                external_message_id: result.external_message_id,
                direction: 'out',
                sender_type: 'agent',
                sender_id: options.agent_id || 'system',
                sender_name: options.agent_name || 'System',
                message_type: options.message_type || 'text',
                content: message,
                status: 'sent'
            });
        }

        return result;
    }

    async handleIncomingMessage(channel, rawMessage) {
        const connector = this.getConnector(channel);
        const normalizedMessage = connector.normalizeIncomingMessage(rawMessage);

        if (!normalizedMessage) {
            return { success: false, error: 'Could not normalize message' };
        }

        let conversation = await this.messageService.findConversation(
            channel,
            normalizedMessage.external_chat_id
        );

        if (!conversation) {
            conversation = await this.messageService.createConversation({
                channel,
                external_chat_id: normalizedMessage.external_chat_id,
                participant_name: normalizedMessage.sender_name,
                participant_phone: normalizedMessage.sender_phone || null
            });
        }

        const savedMessage = await this.messageService.createMessage({
            conversation_id: conversation.id,
            channel,
            external_message_id: normalizedMessage.external_message_id,
            direction: 'in',
            sender_type: 'customer',
            sender_id: normalizedMessage.sender_id,
            sender_name: normalizedMessage.sender_name,
            message_type: normalizedMessage.message_type,
            content: normalizedMessage.content,
            media_url: normalizedMessage.media_url,
            media_type: normalizedMessage.media_type,
            metadata: normalizedMessage.metadata
        });

        const automationResult = await this.processAutomation(normalizedMessage, conversation);

        return {
            success: true,
            message: savedMessage,
            conversation,
            automation: automationResult
        };
    }

    async handleWebhook(channel, payload, signature = null) {
        const connector = this.getConnector(channel);
        const result = await connector.handleWebhook(payload, signature);

        if (!result.success) {
            return result;
        }

        if (result.message) {
            return await this.handleIncomingMessage(channel, result.raw_payload);
        }

        if (result.messages && result.messages.length > 0) {
            const processedMessages = [];
            for (const msg of result.messages) {
                const processed = await this.handleIncomingMessage(channel, msg);
                processedMessages.push(processed);
            }
            return { success: true, processed: processedMessages };
        }

        return result;
    }

    async processAutomation(message, conversation) {
        const results = [];

        for (const rule of this.automationRules) {
            if (this.matchesRule(message, rule)) {
                const actionResult = await this.executeAction(rule.action, message, conversation);
                results.push({
                    rule: rule.name,
                    result: actionResult
                });
            }
        }

        return results;
    }

    matchesRule(message, rule) {
        if (rule.conditions.channel && rule.conditions.channel !== message.channel) {
            return false;
        }

        if (rule.conditions.keywords) {
            const content = message.content.toLowerCase();
            const hasKeyword = rule.conditions.keywords.some(kw =>
                content.includes(kw.toLowerCase())
            );
            if (!hasKeyword) return false;
        }

        if (rule.conditions.message_type && rule.conditions.message_type !== message.message_type) {
            return false;
        }

        return true;
    }

    async executeAction(action, message, conversation) {
        switch (action.type) {
            case 'auto_reply':
                return await this.sendMessage(
                    message.channel,
                    message.external_chat_id,
                    action.message,
                    { conversation_id: conversation.id }
                );

            case 'assign_agent':
                return { success: true, action: 'assign_agent', agent_id: action.agent_id };

            case 'create_lead':
                const LeadService = require('../models/LeadService');
                return await LeadService.createLead({
                    customer_name: message.sender_name,
                    customer_phone: message.sender_phone || 'Не указан',
                    source: message.channel,
                    interest: message.content.substring(0, 200),
                    notes: `Автоматически создан из ${message.channel}`
                });

            case 'notify':
                console.log(`NOTIFICATION: ${action.message}`, { message, conversation });
                return { success: true, action: 'notify' };

            default:
                return { success: false, error: `Unknown action type: ${action.type}` };
        }
    }

    addAutomationRule(rule) {
        if (!rule.name || !rule.conditions || !rule.action) {
            throw new Error('Invalid automation rule: requires name, conditions, and action');
        }
        this.automationRules.push(rule);
        return { success: true, rule_id: this.automationRules.length - 1 };
    }

    removeAutomationRule(ruleIndex) {
        if (ruleIndex >= 0 && ruleIndex < this.automationRules.length) {
            this.automationRules.splice(ruleIndex, 1);
            return { success: true };
        }
        return { success: false, error: 'Rule not found' };
    }

    getAutomationRules() {
        return this.automationRules.map((rule, index) => ({
            id: index,
            ...rule
        }));
    }

    async getConversations(options = {}) {
        return await this.messageService.getConversations(options);
    }

    async getMessages(conversationId, options = {}) {
        return await this.messageService.getMessages(conversationId, options);
    }

    async getAllMessages(options = {}) {
        return await this.messageService.getAllMessages(options);
    }

    async getChannelStats() {
        return await this.messageService.getChannelStats();
    }

    async getUnreadCount(channel = null) {
        return await this.messageService.getUnreadCount(channel);
    }

    async markAsRead(messageId) {
        return await this.messageService.markAsRead(messageId);
    }

    getStatus() {
        return {
            initialized: this.isInitialized,
            connectors: {
                telegram: TelegramConnector.getStatus(),
                wazzup: WazzupConnector.getStatus()
            },
            automation_rules: this.automationRules.length
        };
    }
}

module.exports = new MessagingHub();