const express = require('express');
const MessagingHub = require('../integrations/MessagingHub');
const router = express.Router();

router.get('/status', async (req, res) => {
    try {
        const status = MessagingHub.getStatus();
        res.json({
            success: true,
            status
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.post('/initialize', async (req, res) => {
    try {
        const result = await MessagingHub.initialize();
        res.json({
            success: true,
            result
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/conversations', async (req, res) => {
    try {
        const { channel, status, limit, offset } = req.query;
        const conversations = await MessagingHub.getConversations({
            channel,
            status,
            limit: parseInt(limit) || 50,
            offset: parseInt(offset) || 0
        });

        res.json({
            success: true,
            conversations,
            count: conversations.length
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/conversations/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { limit, offset } = req.query;

        const messages = await MessagingHub.getMessages(id, {
            limit: parseInt(limit) || 50,
            offset: parseInt(offset) || 0
        });

        res.json({
            success: true,
            conversation_id: id,
            messages,
            count: messages.length
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/', async (req, res) => {
    try {
        const { channel, direction, limit, offset } = req.query;
        const messages = await MessagingHub.getAllMessages({
            channel,
            direction,
            limit: parseInt(limit) || 100,
            offset: parseInt(offset) || 0
        });

        res.json({
            success: true,
            messages,
            count: messages.length
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.post('/send', async (req, res) => {
    try {
        const { channel, chat_id, message, options } = req.body;

        if (!channel || !chat_id || !message) {
            return res.status(400).json({
                success: false,
                error: 'channel, chat_id, and message are required'
            });
        }

        const result = await MessagingHub.sendMessage(channel, chat_id, message, options || {});
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.post('/:messageId/read', async (req, res) => {
    try {
        const { messageId } = req.params;
        const result = await MessagingHub.markAsRead(messageId);
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/unread', async (req, res) => {
    try {
        const { channel } = req.query;
        const count = await MessagingHub.getUnreadCount(channel || null);
        res.json({
            success: true,
            unread_count: count,
            channel: channel || 'all'
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/stats', async (req, res) => {
    try {
        const stats = await MessagingHub.getChannelStats();
        res.json({
            success: true,
            stats
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/automation/rules', (req, res) => {
    try {
        const rules = MessagingHub.getAutomationRules();
        res.json({
            success: true,
            rules,
            count: rules.length
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.post('/automation/rules', (req, res) => {
    try {
        const rule = req.body;
        const result = MessagingHub.addAutomationRule(rule);
        res.json(result);
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

router.delete('/automation/rules/:id', (req, res) => {
    try {
        const { id } = req.params;
        const result = MessagingHub.removeAutomationRule(parseInt(id));
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router;