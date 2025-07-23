# TinyProxy Setup Guide for VPS

## Overview
TinyProxy is a lightweight HTTP proxy that will route SAMO API requests from Replit through your VPS server, using your whitelisted IP address.

## VPS Server Setup

### 1. Install TinyProxy

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tinyproxy
```

**CentOS/RHEL:**
```bash
sudo yum install tinyproxy
# or for newer versions:
sudo dnf install tinyproxy
```

### 2. Configure TinyProxy

Edit the configuration file:
```bash
sudo nano /etc/tinyproxy/tinyproxy.conf
```

Key configuration changes:
```conf
# Port to listen on (default 8888)
Port 8888

# Allow connections from Replit IP ranges
# You can specify specific IPs or ranges
Allow 127.0.0.1
Allow 10.0.0.0/8
Allow 172.16.0.0/12
Allow 192.168.0.0/16
# Add Replit's IP ranges (Google Cloud Platform ranges)
Allow 34.0.0.0/8
Allow 35.0.0.0/8

# Optional: Basic authentication
# BasicAuth username password

# Log level (Info, Warning, Error, Critical)
LogLevel Info

# Log file location
LogFile "/var/log/tinyproxy/tinyproxy.log"

# Disable via header (security)
DisableViaHeader Yes

# Filter URLs (optional - restrict to SAMO API only)
# Filter "/etc/tinyproxy/filter"
```

### 3. Create Filter File (Optional)

For extra security, restrict proxy to SAMO API only:
```bash
sudo nano /etc/tinyproxy/filter
```

Add:
```
booking.crystalbay.com
booking-kz.crystalbay.com
```

### 4. Start and Enable TinyProxy

```bash
# Start the service
sudo systemctl start tinyproxy

# Enable auto-start on boot
sudo systemctl enable tinyproxy

# Check status
sudo systemctl status tinyproxy

# View logs
sudo tail -f /var/log/tinyproxy/tinyproxy.log
```

### 5. Firewall Configuration

Open the proxy port:
```bash
# UFW (Ubuntu)
sudo ufw allow 8888

# iptables
sudo iptables -A INPUT -p tcp --dport 8888 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload
```

### 6. Test the Proxy

From your VPS, test that the proxy works:
```bash
# Test direct connection
curl "https://booking.crystalbay.com/export/default.php?samo_action=api&oauth_token=27bd59a7ac67422189789f0188167379&type=json&action=SearchTour_TOWNFROMS"

# Test through proxy
curl --proxy localhost:8888 "https://booking.crystalbay.com/export/default.php?samo_action=api&oauth_token=27bd59a7ac67422189789f0188167379&type=json&action=SearchTour_TOWNFROMS"
```

## Security Considerations

### 1. Basic Authentication (Recommended)

Add to tinyproxy.conf:
```conf
BasicAuth proxy_user your_secure_password
```

### 2. IP Restrictions

Only allow connections from known sources:
```conf
# Remove the broad Allow statements and add specific ones
Allow 34.138.66.105  # Current Replit IP
# Add other known Replit IP ranges as needed
```

### 3. SSL/TLS Termination

For additional security, use nginx as a reverse proxy:
```nginx
server {
    listen 443 ssl;
    server_name proxy.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Replit Configuration

### Environment Variables

Set in Replit secrets:
```
HTTP_PROXY=http://your-vps-ip:8888
HTTPS_PROXY=http://your-vps-ip:8888

# If using authentication:
HTTP_PROXY=http://proxy_user:your_secure_password@your-vps-ip:8888
HTTPS_PROXY=http://proxy_user:your_secure_password@your-vps-ip:8888
```

### Alternative: Direct Proxy Configuration

Instead of environment variables, configure proxy in Python code:
```python
import requests

proxies = {
    'http': 'http://your-vps-ip:8888',
    'https': 'http://your-vps-ip:8888'
}

# With authentication:
proxies = {
    'http': 'http://proxy_user:password@your-vps-ip:8888',
    'https': 'http://proxy_user:password@your-vps-ip:8888'
}

response = requests.get(url, proxies=proxies)
```

## Monitoring and Maintenance

### Log Monitoring
```bash
# Monitor live logs
sudo tail -f /var/log/tinyproxy/tinyproxy.log

# Check for errors
sudo grep -i error /var/log/tinyproxy/tinyproxy.log

# Log rotation (automatic with logrotate)
sudo logrotate -f /etc/logrotate.d/tinyproxy
```

### Health Checks
```bash
# Check service status
sudo systemctl status tinyproxy

# Test connectivity
curl --proxy your-vps-ip:8888 http://httpbin.org/ip
```

## Advantages of TinyProxy Solution

1. **Lightweight**: Minimal resource usage
2. **Transparent**: No code changes needed in applications
3. **Reliable**: Battle-tested proxy server
4. **Secure**: Built-in authentication and filtering
5. **Flexible**: Easy to configure and maintain
6. **Fast**: Direct HTTP proxy without overhead

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if tinyproxy is running: `sudo systemctl status tinyproxy`
   - Verify firewall rules
   - Check port binding: `sudo netstat -tlnp | grep 8888`

2. **Access Denied**
   - Verify Allow rules in config
   - Check authentication settings
   - Review logs for specific errors

3. **SSL Issues**
   - TinyProxy doesn't terminate SSL, it tunnels it
   - Ensure HTTPS_PROXY is set correctly
   - Check certificate validation settings

### Useful Commands
```bash
# Restart service
sudo systemctl restart tinyproxy

# Reload configuration
sudo systemctl reload tinyproxy

# Check configuration syntax
sudo tinyproxy -d -c /etc/tinyproxy/tinyproxy.conf

# Monitor real-time connections
sudo netstat -an | grep :8888
```

This setup will solve your IP whitelist issue by routing all SAMO API requests through your VPS with the approved IP address.