"""
Proxy configuration for SAMO API requests to use static IP
This helps resolve the dynamic IP issue with Replit deployments
"""

import os
import requests
from typing import Dict, Any, Optional

class StaticIPProxy:
    """Proxy service to route SAMO API requests through static IP"""
    
    def __init__(self):
        # Example proxy services that offer static IPs
        self.proxy_services = {
            'quotaguard': {
                'url': os.environ.get('QUOTAGUARD_URL'),
                'description': 'QuotaGuard Static - provides static IPs for Heroku/cloud apps'
            },
            'fixie': {
                'url': os.environ.get('FIXIE_URL'), 
                'description': 'Fixie Socks - static IP proxy service'
            },
            'proxyway': {
                'url': os.environ.get('PROXYWAY_URL'),
                'description': 'ProxyWay - enterprise static IP service'
            }
        }
    
    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """Get available proxy configuration"""
        for service_name, config in self.proxy_services.items():
            if config['url']:
                return {
                    'service': service_name,
                    'proxy_url': config['url'],
                    'description': config['description']
                }
        return None
    
    def make_request_via_proxy(self, url: str, method: str = 'GET', 
                              params: Dict = None, data: str = None, 
                              headers: Dict = None) -> requests.Response:
        """Make HTTP request through proxy with static IP"""
        proxy_config = self.get_proxy_config()
        
        if not proxy_config:
            # Fallback to direct request if no proxy available
            return self._direct_request(url, method, params, data, headers)
        
        proxy_url = proxy_config['proxy_url']
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        if method.upper() == 'GET':
            return requests.get(url, params=params, headers=headers, 
                              proxies=proxies, timeout=10)
        elif method.upper() == 'POST':
            return requests.post(url, params=params, data=data, 
                               headers=headers, proxies=proxies, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def _direct_request(self, url: str, method: str, params: Dict, 
                       data: str, headers: Dict) -> requests.Response:
        """Fallback to direct request without proxy"""
        if method.upper() == 'GET':
            return requests.get(url, params=params, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            return requests.post(url, params=params, data=data, 
                               headers=headers, timeout=10)

def get_static_ip_solutions() -> Dict[str, Any]:
    """Get information about static IP solutions"""
    return {
        'current_issue': {
            'approved_ip': '34.117.33.233',
            'current_ip': '34.138.66.105',
            'status': 'IP mismatch causing 403 Forbidden'
        },
        'solutions': [
            {
                'name': 'QuotaGuard Static',
                'type': 'Proxy Service',
                'description': 'Routes requests through static IP',
                'setup': 'Add QUOTAGUARD_URL environment variable',
                'cost': 'Paid service (~$5-20/month)',
                'reliability': 'High'
            },
            {
                'name': 'Additional IP Whitelist',
                'type': 'Crystal Bay Support Request',
                'description': 'Request whitelisting of current IP',
                'setup': 'Contact Crystal Bay with current IP: 34.138.66.105',
                'cost': 'Free',
                'reliability': 'Medium (IP may change again)'
            },
            {
                'name': 'IP Range Whitelist',
                'type': 'Crystal Bay Support Request', 
                'description': 'Request whitelisting of Replit IP range',
                'setup': 'Contact Crystal Bay for broader IP range approval',
                'cost': 'Free',
                'reliability': 'High (covers future IP changes)'
            }
        ],
        'recommended': 'IP Range Whitelist (most reliable long-term solution)'
    }