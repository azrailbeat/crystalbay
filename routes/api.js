const express = require('express');
const LeadService = require('../models/LeadService');
const BookingService = require('../models/BookingService');
const SettingsService = require('../models/SettingsService');
const { spawn } = require('child_process');
const axios = require('axios');
const router = express.Router();

// Leads API
router.get('/leads', async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 50;
        const leads = await LeadService.getLeads(limit);
        
        res.json({
            success: true,
            leads,
            count: leads.length
        });
    } catch (error) {
        console.error('API get leads error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

router.post('/leads', async (req, res) => {
    try {
        const data = req.body || {};
        
        // Support both field name variations for compatibility
        const customerName = data.customer_name || data.name;
        const customerPhone = data.customer_phone || data.phone;
        
        if (!customerName) {
            return res.status(400).json({
                success: false,
                error: 'Customer name is required'
            });
        }
        
        const leadData = {
            customer_name: customerName,
            customer_phone: customerPhone || 'Не указан',
            customer_email: data.customer_email || data.email || 'Не указан',
            source: data.source || 'website',
            interest: data.interest || data.tour_interest || 'Общий интерес',
            notes: data.notes || data.details || '',
            status: 'new'
        };
        
        const lead = await LeadService.createLead(leadData);
        
        res.json({
            success: true,
            lead_id: lead.id,
            message: 'Lead created successfully'
        });
        
    } catch (error) {
        console.error('API create lead error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

router.get('/chat/history/:leadId', async (req, res) => {
    try {
        const { leadId } = req.params;
        
        // Return empty array for now since chat history is not implemented
        res.json({
            success: true,
            messages: [],
            count: 0,
            lead_id: leadId
        });
    } catch (error) {
        console.error('API get chat history error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            messages: []
        });
    }
});

// Settings API
router.get('/settings/samo', async (req, res) => {
    try {
        const settings = await SettingsService.getSamoSettings();
        res.json({
            success: true,
            settings
        });
    } catch (error) {
        console.error('API get SAMO settings error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

router.post('/settings/samo', async (req, res) => {
    try {
        const data = req.body || {};
        
        // Update each setting
        const updatedSettings = {};
        for (const [key, value] of Object.entries(data)) {
            if (['api_url', 'oauth_token', 'timeout', 'user_agent'].includes(key)) {
                const success = await SettingsService.updateSamoSetting(key, String(value));
                updatedSettings[key] = value;
                if (!success) {
                    console.warn(`Failed to save setting ${key} to database, using memory storage`);
                }
            }
        }
        
        res.json({
            success: true,
            message: 'SAMO settings updated successfully',
            updated_settings: updatedSettings
        });
        
    } catch (error) {
        console.error('API update SAMO settings error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// SAMO API Endpoints
router.get('/samo/currencies', async (req, res) => {
    try {
        const SamoAPI = require('../utils/SamoAPI');
        const samoApi = new SamoAPI();
        const result = await samoApi.getCurrencies();
        res.json(result);
    } catch (error) {
        console.error('Error getting SAMO currencies:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/samo/states', async (req, res) => {
    try {
        const SamoAPI = require('../utils/SamoAPI');
        const samoApi = new SamoAPI();
        const result = await samoApi.getStates();
        res.json(result);
    } catch (error) {
        console.error('Error getting SAMO states:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/samo/townfroms', async (req, res) => {
    try {
        const SamoAPI = require('../utils/SamoAPI');
        const samoApi = new SamoAPI();
        const result = await samoApi.getTownFroms();
        res.json(result);
    } catch (error) {
        console.error('Error getting SAMO townfroms:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/samo/stars', async (req, res) => {
    try {
        const SamoAPI = require('../utils/SamoAPI');
        const samoApi = new SamoAPI();
        const result = await samoApi.getStars();
        res.json(result);
    } catch (error) {
        console.error('Error getting SAMO stars:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/samo/meals', async (req, res) => {
    try {
        const SamoAPI = require('../utils/SamoAPI');
        const samoApi = new SamoAPI();
        const result = await samoApi.getMeals();
        res.json(result);
    } catch (error) {
        console.error('Error getting SAMO meals:', error);
        res.status(500).json({ error: error.message });
    }
});

router.post('/samo/search-tours-new', async (req, res) => {
    try {
        const searchParams = req.body;
        
        const SamoAPI = require('../utils/SamoAPI');
        const samoApi = new SamoAPI();
        const result = await samoApi.searchTourPrices(searchParams);
        
        res.json(result);
    } catch (error) {
        console.error('Error searching SAMO tours:', error);
        res.status(500).json({ error: error.message });
    }
});

// Curl API
router.post('/curl/execute', async (req, res) => {
    try {
        const data = req.body || {};
        const url = data.url || '';
        const method = (data.method || 'GET').toUpperCase();
        const headers = data.headers || {};
        const payload = data.payload || {};
        
        if (!url) {
            return res.status(400).json({
                success: false,
                error: 'URL is required'
            });
        }
        
        // Build curl command
        const curlArgs = ['-s', '-w', '\\nHTTP Status: %{http_code}\\nTime: %{time_total}s\\n'];
        
        // Add method
        if (method !== 'GET') {
            curlArgs.push('-X', method);
        }
        
        // Add headers
        for (const [key, value] of Object.entries(headers)) {
            curlArgs.push('-H', `${key}: ${value}`);
        }
        
        // Add payload for POST/PUT
        if (['POST', 'PUT'].includes(method) && payload) {
            if (typeof payload === 'object') {
                // Form data
                for (const [key, value] of Object.entries(payload)) {
                    curlArgs.push('-d', `${key}=${value}`);
                }
            } else {
                // Raw data
                curlArgs.push('-d', String(payload));
            }
        }
        
        // Add URL
        curlArgs.push(url);
        
        // Execute curl command
        const curl = spawn('curl', curlArgs, { timeout: 30000 });
        let stdout = '';
        let stderr = '';
        
        curl.stdout.on('data', (data) => {
            stdout += data.toString();
        });
        
        curl.stderr.on('data', (data) => {
            stderr += data.toString();
        });
        
        curl.on('close', (code) => {
            res.json({
                success: true,
                command: `curl ${curlArgs.join(' ')}`,
                stdout,
                stderr,
                return_code: code,
                execution_time: '< 30s'
            });
        });
        
        curl.on('error', (error) => {
            res.status(500).json({
                success: false,
                error: error.message
            });
        });
        
    } catch (error) {
        console.error('API execute curl error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

router.post('/curl/generate', async (req, res) => {
    try {
        const data = req.body || {};
        const url = data.url || '';
        const method = (data.method || 'GET').toUpperCase();
        const headers = data.headers || {};
        const payload = data.payload || {};
        
        if (!url) {
            return res.status(400).json({
                success: false,
                error: 'URL is required'
            });
        }
        
        // Build curl command string
        let curlParts = ['curl', '-v'];
        
        // Add method
        if (method !== 'GET') {
            curlParts.push('-X', method);
        }
        
        // Add headers
        for (const [key, value] of Object.entries(headers)) {
            curlParts.push('-H', `"${key}: ${value}"`);
        }
        
        // Add payload for POST/PUT
        if (['POST', 'PUT'].includes(method) && payload) {
            if (typeof payload === 'object') {
                // Form data
                for (const [key, value] of Object.entries(payload)) {
                    curlParts.push('-d', `"${key}=${value}"`);
                }
            } else {
                // Raw data
                curlParts.push('-d', `"${payload}"`);
            }
        }
        
        // Add URL
        curlParts.push(`"${url}"`);
        
        const command = curlParts.join(' ');
        
        res.json({
            success: true,
            command,
            parameters: {
                url,
                method,
                headers,
                payload
            }
        });
        
    } catch (error) {
        console.error('API generate curl error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Diagnostics endpoints
router.get('/diagnostics/environment', (req, res) => {
    try {
        const environment = {
            "SUPABASE_URL": process.env.SUPABASE_URL ? "✓" : "✗ Отсутствует",
            "SUPABASE_KEY": process.env.SUPABASE_KEY ? "✓" : "✗ Отсутствует", 
            "OPENAI_API_KEY": process.env.OPENAI_API_KEY ? "✓" : "✗ Отсутствует",
            "SAMO_OAUTH_TOKEN": process.env.SAMO_OAUTH_TOKEN ? "✓" : "✗ Отсутствует",
            "DATABASE_URL": process.env.DATABASE_URL ? "✓" : "✗ Отсутствует"
        };
        
        res.json({
            timestamp: new Date().toISOString(),
            environment
        });
    } catch (error) {
        console.error('Environment diagnostics error:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/diagnostics/samo', async (req, res) => {
    try {
        const axios = require('axios');
        const dns = require('dns').promises;
        
        const oauthToken = process.env.SAMO_OAUTH_TOKEN || "27bd59a7ac67422189789f0188167379";
        const samoUrl = "https://booking.crystalbay.com/export/default.php";
        
        const diagnostics = {
            timestamp: new Date().toISOString(),
            api_url: samoUrl,
            oauth_token_suffix: oauthToken ? oauthToken.slice(-4) : "None",
            tests: {}
        };
        
        // DNS Test
        try {
            await dns.lookup("booking.crystalbay.com");
            diagnostics.tests.dns_resolution = { status: "✓", message: "DNS работает" };
        } catch (error) {
            diagnostics.tests.dns_resolution = { status: "✗", error: error.message };
        }
        
        // API Test
        try {
            const params = new URLSearchParams({
                samo_action: 'api',
                version: '1.0',
                type: 'json',
                action: 'SearchTour_CURRENCIES',
                oauth_token: oauthToken
            });
            
            const response = await axios.post(samoUrl, params, { timeout: 10000 });
            
            diagnostics.tests.api_endpoint = {
                status: "Tested",
                status_code: response.status,
                response_length: response.data.length || 0,
                response_preview: String(response.data).substring(0, 200)
            };
            
            if (response.status === 403) {
                diagnostics.tests.api_endpoint.message = "403 Forbidden - IP заблокирован или проблема с токеном";
            }
            
        } catch (error) {
            diagnostics.tests.api_endpoint = { status: "✗", error: error.message };
        }
        
        res.json(diagnostics);
        
    } catch (error) {
        console.error('SAMO diagnostics error:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/diagnostics/server', async (req, res) => {
    try {
        // Get external IP
        let externalIp = "Unknown";
        try {
            const response = await axios.get("https://httpbin.org/ip", { timeout: 10000 });
            externalIp = response.data.origin || "Unknown";
        } catch {
            try {
                const response = await axios.get("https://icanhazip.com", { timeout: 10000 });
                externalIp = response.data.trim();
            } catch {
                // Leave as Unknown
            }
        }
        
        res.json({
            timestamp: new Date().toISOString(),
            external_ip: externalIp,
            user_agent: "Crystal Bay Travel Production/1.0",
            node_version: process.version,
            environment_vars_count: Object.keys(process.env).filter(k => !k.startsWith('_')).length
        });
        
    } catch (error) {
        console.error('Server diagnostics error:', error);
        res.status(500).json({ error: error.message });
    }
});

router.get('/diagnostics/curl', (req, res) => {
    try {
        const oauthToken = process.env.SAMO_OAUTH_TOKEN || "27bd59a7ac67422189789f0188167379";
        
        const curlCommand = `curl -X POST 'https://booking.crystalbay.com/export/default.php' \\
  -H 'User-Agent: Crystal Bay Travel Production/1.0' \\
  -H 'Accept: application/json' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token=${oauthToken}' \\
  -v --connect-timeout 15 --max-time 30`;
        
        res.json({ curl_command: curlCommand });
    } catch (error) {
        console.error('Curl generation error:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;