const { Pool } = require('pg');

class MessageService {
    constructor() {
        this.pool = null;
        this.messages = new Map();
        this.conversations = new Map();
        this.initDatabase();
    }

    async initDatabase() {
        try {
            if (process.env.DATABASE_URL) {
                this.pool = new Pool({
                    connectionString: process.env.DATABASE_URL,
                    ssl: { rejectUnauthorized: false }
                });
                await this.createTables();
                console.log('MessageService: Database connection established');
            } else {
                console.warn('MessageService: Using memory storage fallback');
            }
        } catch (error) {
            console.error('MessageService: Database connection failed:', error.message);
        }
    }

    async createTables() {
        if (!this.pool) return;

        const createConversationsTable = `
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR(255) PRIMARY KEY,
                lead_id VARCHAR(255),
                channel VARCHAR(50) NOT NULL,
                external_chat_id VARCHAR(255),
                participant_name VARCHAR(255),
                participant_phone VARCHAR(100),
                status VARCHAR(50) DEFAULT 'active',
                last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}'
            )
        `;

        const createMessagesTable = `
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR(255) PRIMARY KEY,
                conversation_id VARCHAR(255) REFERENCES conversations(id),
                channel VARCHAR(50) NOT NULL,
                external_message_id VARCHAR(255),
                direction VARCHAR(10) NOT NULL,
                sender_type VARCHAR(20) DEFAULT 'customer',
                sender_id VARCHAR(255),
                sender_name VARCHAR(255),
                message_type VARCHAR(50) DEFAULT 'text',
                content TEXT,
                media_url TEXT,
                media_type VARCHAR(50),
                status VARCHAR(50) DEFAULT 'sent',
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}'
            )
        `;

        const createIndexes = `
            CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
            CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_conversations_lead ON conversations(lead_id);
            CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(channel);
        `;

        try {
            await this.pool.query(createConversationsTable);
            await this.pool.query(createMessagesTable);
            await this.pool.query(createIndexes);
            console.log('MessageService: Tables created successfully');
        } catch (error) {
            console.error('MessageService: Error creating tables:', error.message);
        }
    }

    generateId(prefix = 'msg') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async createConversation(data) {
        const id = this.generateId('conv');
        const conversation = {
            id,
            lead_id: data.lead_id || null,
            channel: data.channel || 'unknown',
            external_chat_id: data.external_chat_id || null,
            participant_name: data.participant_name || 'Unknown',
            participant_phone: data.participant_phone || null,
            status: 'active',
            last_message_at: new Date().toISOString(),
            created_at: new Date().toISOString(),
            metadata: data.metadata || {}
        };

        if (this.pool) {
            try {
                await this.pool.query(
                    `INSERT INTO conversations (id, lead_id, channel, external_chat_id, participant_name, participant_phone, status, last_message_at, created_at, metadata)
                     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
                    [conversation.id, conversation.lead_id, conversation.channel, conversation.external_chat_id,
                     conversation.participant_name, conversation.participant_phone, conversation.status,
                     conversation.last_message_at, conversation.created_at, JSON.stringify(conversation.metadata)]
                );
            } catch (error) {
                console.error('Error saving conversation:', error.message);
            }
        }

        this.conversations.set(id, conversation);
        return conversation;
    }

    async getConversation(id) {
        if (this.pool) {
            try {
                const result = await this.pool.query('SELECT * FROM conversations WHERE id = $1', [id]);
                if (result.rows.length > 0) {
                    return result.rows[0];
                }
            } catch (error) {
                console.error('Error getting conversation:', error.message);
            }
        }
        return this.conversations.get(id) || null;
    }

    async findConversation(channel, externalChatId) {
        if (this.pool) {
            try {
                const result = await this.pool.query(
                    'SELECT * FROM conversations WHERE channel = $1 AND external_chat_id = $2 ORDER BY created_at DESC LIMIT 1',
                    [channel, externalChatId]
                );
                if (result.rows.length > 0) {
                    return result.rows[0];
                }
            } catch (error) {
                console.error('Error finding conversation:', error.message);
            }
        }

        for (const conv of this.conversations.values()) {
            if (conv.channel === channel && conv.external_chat_id === externalChatId) {
                return conv;
            }
        }
        return null;
    }

    async getConversations(options = {}) {
        const { channel, status, limit = 50, offset = 0 } = options;

        if (this.pool) {
            try {
                let query = 'SELECT * FROM conversations WHERE 1=1';
                const params = [];
                let paramIndex = 1;

                if (channel) {
                    query += ` AND channel = $${paramIndex++}`;
                    params.push(channel);
                }
                if (status) {
                    query += ` AND status = $${paramIndex++}`;
                    params.push(status);
                }

                query += ` ORDER BY last_message_at DESC LIMIT $${paramIndex++} OFFSET $${paramIndex}`;
                params.push(limit, offset);

                const result = await this.pool.query(query, params);
                return result.rows;
            } catch (error) {
                console.error('Error getting conversations:', error.message);
            }
        }

        let conversations = Array.from(this.conversations.values());
        if (channel) {
            conversations = conversations.filter(c => c.channel === channel);
        }
        if (status) {
            conversations = conversations.filter(c => c.status === status);
        }
        return conversations.slice(offset, offset + limit);
    }

    async createMessage(data) {
        const id = this.generateId('msg');
        const message = {
            id,
            conversation_id: data.conversation_id,
            channel: data.channel || 'unknown',
            external_message_id: data.external_message_id || null,
            direction: data.direction || 'in',
            sender_type: data.sender_type || 'customer',
            sender_id: data.sender_id || null,
            sender_name: data.sender_name || 'Unknown',
            message_type: data.message_type || 'text',
            content: data.content || '',
            media_url: data.media_url || null,
            media_type: data.media_type || null,
            status: data.status || 'sent',
            read_at: null,
            created_at: new Date().toISOString(),
            metadata: data.metadata || {}
        };

        if (this.pool) {
            try {
                await this.pool.query(
                    `INSERT INTO messages (id, conversation_id, channel, external_message_id, direction, sender_type, sender_id, sender_name, message_type, content, media_url, media_type, status, created_at, metadata)
                     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)`,
                    [message.id, message.conversation_id, message.channel, message.external_message_id,
                     message.direction, message.sender_type, message.sender_id, message.sender_name,
                     message.message_type, message.content, message.media_url, message.media_type,
                     message.status, message.created_at, JSON.stringify(message.metadata)]
                );

                await this.pool.query(
                    'UPDATE conversations SET last_message_at = $1 WHERE id = $2',
                    [message.created_at, message.conversation_id]
                );
            } catch (error) {
                console.error('Error saving message:', error.message);
            }
        }

        this.messages.set(id, message);
        return message;
    }

    async getMessages(conversationId, options = {}) {
        const { limit = 50, offset = 0 } = options;

        if (this.pool) {
            try {
                const result = await this.pool.query(
                    'SELECT * FROM messages WHERE conversation_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3',
                    [conversationId, limit, offset]
                );
                return result.rows;
            } catch (error) {
                console.error('Error getting messages:', error.message);
            }
        }

        return Array.from(this.messages.values())
            .filter(m => m.conversation_id === conversationId)
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(offset, offset + limit);
    }

    async getAllMessages(options = {}) {
        const { channel, direction, limit = 100, offset = 0 } = options;

        if (this.pool) {
            try {
                let query = 'SELECT m.*, c.participant_name, c.participant_phone FROM messages m LEFT JOIN conversations c ON m.conversation_id = c.id WHERE 1=1';
                const params = [];
                let paramIndex = 1;

                if (channel) {
                    query += ` AND m.channel = $${paramIndex++}`;
                    params.push(channel);
                }
                if (direction) {
                    query += ` AND m.direction = $${paramIndex++}`;
                    params.push(direction);
                }

                query += ` ORDER BY m.created_at DESC LIMIT $${paramIndex++} OFFSET $${paramIndex}`;
                params.push(limit, offset);

                const result = await this.pool.query(query, params);
                return result.rows;
            } catch (error) {
                console.error('Error getting all messages:', error.message);
            }
        }

        let messages = Array.from(this.messages.values());
        if (channel) {
            messages = messages.filter(m => m.channel === channel);
        }
        if (direction) {
            messages = messages.filter(m => m.direction === direction);
        }
        return messages.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(offset, offset + limit);
    }

    async markAsRead(messageId) {
        const readAt = new Date().toISOString();

        if (this.pool) {
            try {
                await this.pool.query(
                    'UPDATE messages SET read_at = $1, status = $2 WHERE id = $3',
                    [readAt, 'read', messageId]
                );
            } catch (error) {
                console.error('Error marking message as read:', error.message);
            }
        }

        const message = this.messages.get(messageId);
        if (message) {
            message.read_at = readAt;
            message.status = 'read';
        }
        return { success: true };
    }

    async getUnreadCount(channel = null) {
        if (this.pool) {
            try {
                let query = 'SELECT COUNT(*) as count FROM messages WHERE read_at IS NULL AND direction = $1';
                const params = ['in'];

                if (channel) {
                    query += ' AND channel = $2';
                    params.push(channel);
                }

                const result = await this.pool.query(query, params);
                return parseInt(result.rows[0].count, 10);
            } catch (error) {
                console.error('Error getting unread count:', error.message);
            }
        }

        let messages = Array.from(this.messages.values()).filter(m => m.direction === 'in' && !m.read_at);
        if (channel) {
            messages = messages.filter(m => m.channel === channel);
        }
        return messages.length;
    }

    async getChannelStats() {
        const channels = ['telegram', 'whatsapp', 'wazzup', 'email', 'sms'];
        const stats = {};

        for (const channel of channels) {
            const conversations = await this.getConversations({ channel, limit: 1000 });
            const unreadCount = await this.getUnreadCount(channel);

            stats[channel] = {
                total_conversations: conversations.length,
                unread_messages: unreadCount,
                status: 'active'
            };
        }

        return stats;
    }
}

module.exports = new MessageService();