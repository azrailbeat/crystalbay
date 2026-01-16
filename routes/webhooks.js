const express = require('express');
const MessagingHub = require('../integrations/MessagingHub');
const TelegramConnector = require('../integrations/TelegramConnector');
const WazzupConnector = require('../integrations/WazzupConnector');
const router = express.Router();

router.post('/telegram', async (req, res) => {
    try {
        const payload = req.body;
        console.log('Telegram webhook received:', JSON.stringify(payload).substring(0, 200));

        const result = await MessagingHub.handleWebhook('telegram', payload);

        res.json({ ok: true, result });
    } catch (error) {
        console.error('Telegram webhook error:', error);
        res.status(500).json({ ok: false, error: error.message });
    }
});

router.post('/telegram/set', async (req, res) => {
    try {
        const { url } = req.body;

        if (!url) {
            return res.status(400).json({
                success: false,
                error: 'Webhook URL is required'
            });
        }

        const result = await TelegramConnector.setWebhook(url);
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.delete('/telegram', async (req, res) => {
    try {
        const result = await TelegramConnector.deleteWebhook();
        res.json(result);
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.post('/wazzup', async (req, res) => {
    try {
        const payload = req.body;
        const signature = req.headers['x-wazzup-signature'] || null;

        console.log('Wazzup webhook received:', JSON.stringify(payload).substring(0, 200));

        const result = await MessagingHub.handleWebhook('wazzup', payload, signature);

        res.json({ success: true, result });
    } catch (error) {
        console.error('Wazzup webhook error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/wazzup/test', async (req, res) => {
    try {
        const status = WazzupConnector.getStatus();
        res.json({
            success: true,
            status,
            message: 'Wazzup webhook endpoint is ready'
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

router.post('/whatsapp', async (req, res) => {
    try {
        const payload = req.body;

        console.log('WhatsApp webhook received:', JSON.stringify(payload).substring(0, 200));

        const result = await MessagingHub.handleWebhook('whatsapp', payload);

        res.json({ success: true, result });
    } catch (error) {
        console.error('WhatsApp webhook error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

router.get('/status', (req, res) => {
    res.json({
        success: true,
        webhooks: {
            telegram: {
                endpoint: '/webhooks/telegram',
                method: 'POST',
                status: TelegramConnector.isConnected ? 'active' : 'inactive'
            },
            wazzup: {
                endpoint: '/webhooks/wazzup',
                method: 'POST',
                status: WazzupConnector.isConnected ? 'active' : 'inactive'
            },
            whatsapp: {
                endpoint: '/webhooks/whatsapp',
                method: 'POST',
                status: 'via_wazzup'
            }
        }
    });
});

module.exports = router;