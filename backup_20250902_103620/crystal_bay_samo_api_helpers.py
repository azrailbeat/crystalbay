"""
Helper functions for Crystal Bay SAMO API error handling
"""

def handle_error_response(response, action, extra_data=None):
    """Унифицированная обработка ошибок ответов SAMO API"""
    extra_data = extra_data or {}
    
    if response.status_code == 403:
        error_text = response.text
        blocked_ip = "Unknown"
        if "blacklisted address" in error_text:
            import re
            ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', error_text)
            blocked_ip = ip_match.group(1) if ip_match else "Unknown"
        
        return {
            "success": False,
            "error": f"IP {blocked_ip} blocked by SAMO API",
            "raw_response": error_text,
            "status_code": 403,
            "action": action,
            "blocked_ip": blocked_ip,
            **extra_data
        }
    elif response.status_code == 500:
        return {
            "success": False,
            "error": "SAMO API Internal Server Error",
            "raw_response": response.text[:500],
            "status_code": 500,
            "action": action,
            "help": "Check required parameters for this action",
            **extra_data
        }
    else:
        return {
            "success": False,
            "error": f"HTTP {response.status_code} {response.reason}",
            "raw_response": response.text[:500],
            "status_code": response.status_code,
            "action": action,
            **extra_data
        }