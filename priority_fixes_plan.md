# Priority Fixes Plan - Crystal Bay Travel System

## Immediate Critical Fixes (Today)

### 1. Fix Type Safety Errors (36 LSP Diagnostics)

**High Priority Fixes:**
```python
# Fix missing imports in main.py
from api_integration import SamoAPIIntegration as APIIntegration  
from models import LeadService
from bitrix_integration import get_bitrix_client as bitrix_client

# Fix null pointer access
if config and hasattr(config, 'get'):
    value = config.get('key')
else:
    value = default_value

# Fix unbound variables
xml_data = ""  # Initialize before conditional usage
```

### 2. Security Hardening

**Immediate Actions:**
```python
# Restrict CORS
from flask_cors import CORS
CORS(app, origins=['https://crystalbay.travel'])

# Add input validation
from cerberus import Validator

def validate_json_input(schema):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            validator = Validator(schema)
            if not validator.validate(request.json):
                return jsonify({'error': 'Invalid input', 'details': validator.errors}), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Add rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 3. Error Handling Standardization

**Standardized Error Response:**
```python
def create_error_response(message, code=400, details=None):
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat(),
        'code': code
    }
    if details:
        response['details'] = details
    return jsonify(response), code

def create_success_response(data=None, message="Success"):
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    if data:
        response['data'] = data
    return jsonify(response)
```

## Short-term Improvements (This Week)

### 4. Database Consistency

**Unified Data Access Layer:**
```python
class DataAccessLayer:
    def __init__(self):
        self.supabase = supabase
        self.memory_store = {}
        self.file_store_path = "data/"
    
    def get_lead(self, lead_id):
        # Try Supabase first, fallback to memory/file
        try:
            if self.supabase:
                return self.supabase.table('leads').select('*').eq('id', lead_id).execute()
        except Exception as e:
            logger.warning(f"Database unavailable, using fallback: {e}")
        
        # Fallback to memory or file storage
        return self._get_from_fallback(lead_id)
```

### 5. Performance Optimization

**Add Caching Layer:**
```python
from flask_caching import Cache
from functools import wraps

# Initialize cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Cache decorator for expensive operations
def cache_result(timeout=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cache_key = f"{f.__name__}_{hash(str(args))}"
            result = cache.get(cache_key)
            if result is None:
                result = f(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator

# Apply to expensive SAMO API calls
@cache_result(timeout=600)  # 10 minute cache
def get_samo_tours(destination, departure_date):
    return samo_api.search_tours(destination, departure_date)
```

### 6. Health Check System

**System Health Monitoring:**
```python
@app.route('/health')
def health_check():
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.2.0',
        'services': {}
    }
    
    # Check Supabase
    try:
        supabase.table('leads').select('id').limit(1).execute()
        health_status['services']['database'] = 'healthy'
    except:
        health_status['services']['database'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    # Check SAMO API
    try:
        samo_response = requests.get(samo_api_url, timeout=5)
        health_status['services']['samo_api'] = 'healthy' if samo_response.status_code == 403 else 'unhealthy'
    except:
        health_status['services']['samo_api'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
```

## Medium-term Refactoring (2 Weeks)

### 7. Break Down main.py

**Service Layer Architecture:**
```
services/
├── lead_service.py
├── booking_service.py
├── integration_service.py
├── notification_service.py
└── auth_service.py

routes/
├── api_routes.py
├── lead_routes.py
├── booking_routes.py
└── admin_routes.py
```

### 8. Testing Infrastructure

**Basic Test Setup:**
```python
# tests/test_samo_integration.py
import pytest
from unittest.mock import Mock, patch
from api_integration import SamoAPIIntegration

class TestSamoIntegration:
    def setup_method(self):
        self.samo = SamoAPIIntegration()
    
    @patch('requests.get')
    def test_get_tours_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'tours': []}
        mock_get.return_value = mock_response
        
        result = self.samo.get_tours('Vietnam')
        assert 'tours' in result
```

## Implementation Order

1. **Day 1**: Fix LSP type errors, add null checks
2. **Day 2**: Implement security measures (CORS, rate limiting)
3. **Day 3**: Standardize error handling across all endpoints
4. **Day 4**: Add health check system and monitoring
5. **Week 2**: Database consistency and caching implementation
6. **Week 3**: Begin main.py refactoring into service layers
7. **Week 4**: Implement testing framework and documentation

## Success Metrics

- ✅ Zero LSP type errors
- ✅ All API endpoints return consistent error formats
- ✅ Health check endpoint operational
- ✅ Response time < 200ms for cached requests
- ✅ Security headers in all responses
- ✅ 95%+ uptime monitoring

## Risk Mitigation

1. **Backup current working system** before major changes
2. **Test each fix in isolation** to avoid breaking existing functionality
3. **Gradual rollout** of new features with feature flags
4. **Monitor logs closely** during implementation phase
5. **Have rollback plan** for each major change

---
*Priority Fixes Plan - Updated July 22, 2025*