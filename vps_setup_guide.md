# VPS SAMO API Proxy Setup Guide

## Overview

Your VPS server has successful access to Crystal Bay's SAMO API, as demonstrated by your test. We can use it as a proxy to route requests from Replit through your VPS.

## VPS Server Setup

### 1. Create Proxy Script on Your VPS

Create a file `/var/www/samo-proxy/index.php` or similar:

```php
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

// Get JSON input
$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON input']);
    exit;
}

// Validate API key (optional security)
$expected_key = 'your-secret-api-key';
if (isset($input['api_key']) && $input['api_key'] !== $expected_key) {
    http_response_code(403);
    echo json_encode(['error' => 'Invalid API key']);
    exit;
}

// Extract request details
$target_url = $input['target_url'] ?? '';
$method = $input['method'] ?? 'GET';
$params = $input['params'] ?? [];
$data = $input['data'] ?? null;
$headers = $input['headers'] ?? [];

if (empty($target_url)) {
    http_response_code(400);
    echo json_encode(['error' => 'target_url required']);
    exit;
}

// Initialize cURL
$ch = curl_init();

if ($method === 'GET') {
    $url = $target_url . '?' . http_build_query($params);
    curl_setopt($ch, CURLOPT_URL, $url);
} else {
    curl_setopt($ch, CURLOPT_URL, $target_url . '?' . http_build_query($params));
    curl_setopt($ch, CURLOPT_POST, true);
    if ($data) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    }
}

// Set headers
if (!empty($headers)) {
    $header_array = [];
    foreach ($headers as $key => $value) {
        $header_array[] = "$key: $value";
    }
    curl_setopt($ch, CURLOPT_HTTPHEADER, $header_array);
}

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

// Execute request
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    http_response_code(500);
    echo json_encode(['error' => 'cURL error: ' . $error]);
} else {
    http_response_code($http_code);
    echo $response;
}
?>
```

### 2. Alternative Node.js Implementation

If you prefer Node.js, create `samo-proxy.js`:

```javascript
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const app = express();

app.use(cors());
app.use(express.json());

const API_KEY = 'your-secret-api-key';

app.post('/samo-proxy', async (req, res) => {
    try {
        const { target_url, method, params, data, headers, api_key } = req.body;
        
        // Validate API key
        if (api_key !== API_KEY) {
            return res.status(403).json({ error: 'Invalid API key' });
        }
        
        if (!target_url) {
            return res.status(400).json({ error: 'target_url required' });
        }
        
        const config = {
            method: method || 'GET',
            url: target_url,
            params: params || {},
            timeout: 30000
        };
        
        if (data) {
            config.data = data;
        }
        
        if (headers) {
            config.headers = headers;
        }
        
        const response = await axios(config);
        res.json(response.data);
        
    } catch (error) {
        console.error('Proxy error:', error.message);
        res.status(500).json({ 
            error: error.message,
            details: error.response?.data || 'No additional details'
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`SAMO proxy server running on port ${PORT}`);
});
```

### 3. Nginx Configuration (if using web server)

Add to your Nginx config:

```nginx
location /samo-proxy {
    # For PHP
    try_files $uri $uri/ /samo-proxy/index.php;
    
    # For Node.js (proxy to port 3000)
    # proxy_pass http://localhost:3000/samo-proxy;
    # proxy_set_header Host $host;
    # proxy_set_header X-Real-IP $remote_addr;
}
```

## Replit Configuration

### Environment Variables

Set these in your Replit secrets:

```
VPS_PROXY_URL=https://your-vps-domain.com/samo-proxy
VPS_API_KEY=your-secret-api-key
```

### Testing

1. Deploy the proxy script on your VPS
2. Set the environment variables in Replit
3. Test the connection using the SAMO testing interface

## Security Considerations

1. **API Key**: Use a strong API key to prevent unauthorized access
2. **Rate Limiting**: Implement rate limiting on your VPS
3. **HTTPS**: Ensure your VPS uses HTTPS
4. **Firewall**: Restrict access to your proxy endpoint
5. **Logging**: Monitor proxy usage for security

## Benefits

- ✅ Uses your approved IP address (from VPS)
- ✅ Reliable connection to SAMO API
- ✅ No dependency on Replit's dynamic IPs
- ✅ Full control over proxy configuration
- ✅ Can cache responses for better performance

## Next Steps

1. Choose implementation (PHP or Node.js)
2. Deploy proxy script on your VPS
3. Configure domain/subdomain
4. Set Replit environment variables
5. Test the integration