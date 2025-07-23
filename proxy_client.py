"""
HTTP Proxy Client for SAMO API requests via TinyProxy on VPS
Routes all SAMO API calls through user's VPS server with whitelisted IP
"""

import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TinyProxyClient:
    """Client for making SAMO API requests through TinyProxy on VPS"""
    
    def __init__(self):
        # Proxy configuration from environment
        self.proxy_host = os.environ.get('PROXY_HOST', '')
        self.proxy_port = os.environ.get('PROXY_PORT', '8888')
        self.proxy_user = os.environ.get('PROXY_USER', '')
        self.proxy_pass = os.environ.get('PROXY_PASS', '')
        
        # SAMO API configuration
        self.samo_base_url = "https://booking.crystalbay.com/export/default.php"
        self.oauth_token = "27bd59a7ac67422189789f0188167379"
        
        # Build proxy URLs
        self.proxies = self._build_proxy_config()
    
    def _build_proxy_config(self) -> Dict[str, str]:
        """Build proxy configuration for requests"""
        if not self.proxy_host:
            logger.warning("No proxy host configured, requests will go direct")
            return {}
        
        # Build proxy URL with or without authentication
        if self.proxy_user and self.proxy_pass:
            proxy_url = f"http://{self.proxy_user}:{self.proxy_pass}@{self.proxy_host}:{self.proxy_port}"
        else:
            proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def is_configured(self) -> bool:
        """Check if proxy is properly configured"""
        return bool(self.proxy_host and self.proxy_port)
    
    def test_proxy_connection(self) -> Dict[str, Any]:
        """Test proxy connectivity"""
        if not self.is_configured():
            return {
                'status': 'not_configured',
                'message': 'Proxy not configured. Set PROXY_HOST environment variable.'
            }
        
        try:
            # Test with a simple HTTP request
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=self.proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_ip = data.get('origin', 'Unknown')
                
                return {
                    'status': 'connected',
                    'message': f'Proxy working correctly',
                    'detected_ip': detected_ip,
                    'proxy_config': f"{self.proxy_host}:{self.proxy_port}"
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Proxy returned {response.status_code}'
                }
                
        except requests.exceptions.ProxyError as e:
            return {
                'status': 'proxy_error',
                'message': f'Proxy connection failed: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}'
            }
    
    def make_samo_request(self, action: str, method: str = 'GET', 
                         params: Dict = None, xml_data: str = None) -> Dict[str, Any]:
        """
        Make SAMO API request through TinyProxy
        
        Args:
            action: SAMO API action (e.g., 'SearchTour_TOWNFROMS')
            method: HTTP method ('GET' or 'POST')
            params: Additional parameters
            xml_data: XML data for POST requests
            
        Returns:
            Dict containing API response or error
        """
        try:
            # Prepare base parameters
            samo_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': action
            }
            
            # Add additional parameters
            if params:
                samo_params.update(params)
            
            # Make request through proxy
            if method.upper() == 'GET':
                response = requests.get(
                    self.samo_base_url,
                    params=samo_params,
                    proxies=self.proxies,
                    timeout=30
                )
            else:
                headers = {'Content-Type': 'application/xml'} if xml_data else {}
                response = requests.post(
                    self.samo_base_url,
                    params=samo_params,
                    data=xml_data,
                    headers=headers,
                    proxies=self.proxies,
                    timeout=30
                )
            
            logger.info(f"SAMO API request via proxy: {action}, Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'SAMO API returned {response.status_code}',
                    'message': response.text[:200] if response.text else 'No response body',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.ProxyError as e:
            logger.error(f"Proxy error for SAMO request {action}: {e}")
            return {
                'error': 'Proxy connection failed',
                'message': str(e),
                'suggestion': 'Check TinyProxy service on VPS'
            }
        except Exception as e:
            logger.error(f"SAMO API request failed {action}: {e}")
            return {
                'error': str(e),
                'message': 'SAMO API request failed'
            }
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get current proxy configuration status"""
        return {
            'configured': self.is_configured(),
            'proxy_host': self.proxy_host or 'Not set',
            'proxy_port': self.proxy_port,
            'auth_enabled': bool(self.proxy_user and self.proxy_pass),
            'environment_vars': {
                'PROXY_HOST': 'Set' if self.proxy_host else 'Missing',
                'PROXY_PORT': 'Set' if self.proxy_port else 'Missing (default: 8888)',
                'PROXY_USER': 'Set' if self.proxy_user else 'Not set (optional)',
                'PROXY_PASS': 'Set' if self.proxy_pass else 'Not set (optional)'
            }
        }

# Global proxy client instance
proxy_client = TinyProxyClient()

def get_proxy_client() -> TinyProxyClient:
    """Get proxy client instance"""
    return proxy_client