const express = require('express');
const LeadService = require('../models/LeadService');
const router = express.Router();

// Helper function to get dashboard data
async function getDashboardData() {
    try {
        const leads = await LeadService.getLeads(10);
        
        const leadStats = {
            total: leads.length,
            new: leads.filter(l => l.status === 'new').length,
            contacted: leads.filter(l => l.status === 'contacted').length,
            qualified: leads.filter(l => l.status === 'qualified').length
        };

        return {
            leads: leads.slice(0, 10),
            stats: leadStats,
            total_leads: leads.length,
            active_leads: leads.filter(l => ['new', 'contacted', 'qualified'].includes(l.status)).length,
            conversion_rate: leads.length > 0 ? (leads.filter(l => l.status === 'qualified').length / leads.length) * 100 : 0,
            samo_status: process.env.SAMO_OAUTH_TOKEN ? 'connected' : 'disconnected'
        };
    } catch (error) {
        console.error('Dashboard data error:', error);
        return {
            leads: [],
            stats: { total: 0, new: 0, contacted: 0, qualified: 0 },
            total_leads: 0,
            active_leads: 0,
            conversion_rate: 0,
            samo_status: 'disconnected'
        };
    }
}

// Main routes
router.get('/', async (req, res) => {
    const dashboardData = await getDashboardData();
    res.render('dashboard', { 
        active_page: 'dashboard',
        dashboard_data: dashboardData
    });
});

router.get('/dashboard', async (req, res) => {
    const dashboardData = await getDashboardData();
    res.render('dashboard', { 
        active_page: 'dashboard',
        dashboard_data: dashboardData
    });
});

router.get('/leads', async (req, res) => {
    try {
        const leads = await LeadService.getLeads(100);
        res.render('leads', { 
            leads,
            active_page: 'leads'
        });
    } catch (error) {
        console.error('Leads page error:', error);
        res.render('error', { 
            error: error.message,
            error_code: 500,
            active_page: 'error'
        });
    }
});

router.get('/wazzup', (req, res) => {
    res.render('wazzup_integration', { active_page: 'wazzup' });
});

router.get('/tours', (req, res) => {
    res.render('tours', { active_page: 'tours' });
});

router.get('/tours-search', (req, res) => {
    res.render('tours_search', { active_page: 'tours-search' });
});

router.get('/bookings', (req, res) => {
    res.render('bookings', { active_page: 'bookings' });
});

router.get('/agents', (req, res) => {
    res.render('agents', { active_page: 'agents' });
});

router.get('/analytics', (req, res) => {
    res.render('analytics', { active_page: 'analytics' });
});

router.get('/history', (req, res) => {
    res.render('history', { active_page: 'history' });
});

router.get('/agents-ai', (req, res) => {
    res.render('ai_agents', { active_page: 'agents-ai' });
});

router.get('/unified-settings', (req, res) => {
    res.render('unified_settings', { active_page: 'settings' });
});

router.get('/samo-testing', (req, res) => {
    res.render('samo_testing', { active_page: 'samo-testing' });
});

router.get('/samo-api', (req, res) => {
    res.redirect('/samo-testing');
});

router.get('/messages', (req, res) => {
    res.render('messages', { active_page: 'messages' });
});

router.get('/settings', (req, res) => {
    res.redirect('/unified-settings');
});

module.exports = router;