"""
VPS Proxy for SAMO API requests
Routes requests through user's VPS server which has whitelisted IP access
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class VPSProxy:
    """Proxy SAMO API requests through user's VPS server"""
    
    def __init__(self):
        # VPS server configuration
        self.vps_endpoint = os.environ.get('VPS_PROXY_URL', 'http://your-vps-server.com/samo-proxy')
        self.vps_api_key = os.environ.get('VPS_API_KEY', '')
        
        # SAMO API configuration
        self.samo_base_url = "https://booking.crystalbay.com/export/default.php"
        self.oauth_token = "27bd59a7ac67422189789f0188167379"
    
    def make_samo_request(self, action: str, method: str = 'GET', 
                         params: Dict = None, xml_data: str = None) -> Dict[str, Any]:
        """
        Make SAMO API request through VPS proxy
        
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
            
            # Check if VPS proxy is configured
            if self.vps_endpoint and self.vps_endpoint != 'http://your-vps-server.com/samo-proxy':
                return self._request_via_vps(samo_params, method, xml_data)
            else:
                # Fallback to direct request (will likely get 403)
                return self._direct_request(samo_params, method, xml_data)
                
        except Exception as e:
            logger.error(f"VPS proxy error: {e}")
            return {
                'error': str(e),
                'message': 'Failed to make request through VPS proxy'
            }
    
    def _request_via_vps(self, params: Dict, method: str, xml_data: str = None) -> Dict[str, Any]:
        """Make request through VPS proxy"""
        try:
            proxy_payload = {
                'target_url': self.samo_base_url,
                'method': method,
                'params': params,
                'headers': {'Content-Type': 'application/xml'} if xml_data else {},
                'data': xml_data,
                'api_key': self.vps_api_key
            }
            
            response = requests.post(
                self.vps_endpoint,
                json=proxy_payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'VPS proxy returned {response.status_code}',
                    'message': response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"VPS request failed: {e}")
            return {
                'error': str(e),
                'message': 'VPS proxy request failed'
            }
    
    def _direct_request(self, params: Dict, method: str, xml_data: str = None) -> Dict[str, Any]:
        """Direct request to SAMO API (fallback)"""
        try:
            if method.upper() == 'GET':
                response = requests.get(self.samo_base_url, params=params, timeout=10)
            else:
                headers = {'Content-Type': 'application/xml'} if xml_data else {}
                response = requests.post(
                    self.samo_base_url, 
                    params=params, 
                    data=xml_data,
                    headers=headers,
                    timeout=10
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'SAMO API returned {response.status_code}',
                    'message': f'Direct request failed - IP not whitelisted',
                    'response_text': response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"Direct SAMO request failed: {e}")
            return {
                'error': str(e),
                'message': 'Direct SAMO API request failed'
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test VPS proxy connection"""
        try:
            if not self.vps_endpoint or self.vps_endpoint == 'http://your-vps-server.com/samo-proxy':
                return {
                    'status': 'not_configured',
                    'message': 'VPS proxy not configured. Set VPS_PROXY_URL environment variable.'
                }
            
            # Test with simple TOWNFROMS request
            result = self.make_samo_request('SearchTour_TOWNFROMS')
            
            if 'error' not in result and 'SearchTour_TOWNFROMS' in result:
                return {
                    'status': 'connected',
                    'message': 'VPS proxy working correctly',
                    'data_count': len(result.get('SearchTour_TOWNFROMS', []))
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('message', 'Unknown error'),
                    'error': result.get('error', 'No error details')
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# Global VPS proxy instance
vps_proxy = VPSProxy()

def get_vps_proxy() -> VPSProxy:
    """Get VPS proxy instance"""
    return vps_proxy