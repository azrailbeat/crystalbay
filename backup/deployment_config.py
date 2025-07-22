#!/usr/bin/env python3
"""
Production Deployment Configuration for Crystal Bay Travel
Validates all production requirements and removes dev/mock dependencies
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

class ProductionValidator:
    """Validates system is ready for production deployment"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.required_env_vars = [
            'SAMO_OAUTH_TOKEN',
            'OPENAI_API_KEY',
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'TELEGRAM_BOT_TOKEN'
        ]
        self.optional_env_vars = [
            'SENDGRID_API_KEY',
            'WAZZUP_API_KEY',
            'BITRIX_WEBHOOK_URL'
        ]
    
    def validate_environment(self):
        """Validate all required environment variables"""
        missing_required = []
        missing_optional = []
        
        for var in self.required_env_vars:
            if not os.environ.get(var):
                missing_required.append(var)
        
        for var in self.optional_env_vars:
            if not os.environ.get(var):
                missing_optional.append(var)
        
        if missing_required:
            self.errors.extend([f"Missing required environment variable: {var}" for var in missing_required])
        
        if missing_optional:
            self.warnings.extend([f"Optional environment variable not set: {var}" for var in missing_optional])
        
        return len(missing_required) == 0
    
    def validate_samo_configuration(self):
        """Validate SAMO API configuration"""
        oauth_token = os.environ.get('SAMO_OAUTH_TOKEN')
        
        if not oauth_token:
            self.errors.append("SAMO_OAUTH_TOKEN is required for production")
            return False
        
        if oauth_token != '27bd59a7ac67422189789f0188167379':
            self.warnings.append("SAMO_OAUTH_TOKEN differs from expected Crystal Bay token")
        
        # Test SAMO connectivity
        try:
            from crystal_bay_samo_api import get_crystal_bay_api
            api = get_crystal_bay_api()
            result = api.get_currencies()
            
            if 'error' in result:
                error_msg = result['error']
                if 'Forbidden' in error_msg or '403' in error_msg:
                    self.warnings.append(f"SAMO API IP not whitelisted (403 Forbidden)")
                else:
                    self.errors.append(f"SAMO API error: {error_msg}")
                return False
            else:
                logger.info("SAMO API connection successful")
                return True
                
        except Exception as e:
            self.errors.append(f"SAMO API connection test failed: {e}")
            return False
    
    def validate_data_sources(self):
        """Ensure no mock data is used in production"""
        mock_indicators = []
        
        # Check if api_integration still has mock modes
        try:
            from api_integration import SamoAPIIntegration
            api = SamoAPIIntegration()
            if hasattr(api, 'use_mocks') and getattr(api, 'use_mocks', False):
                mock_indicators.append("API Integration still using mock mode")
            else:
                logger.info("API Integration configured for production mode")
        except Exception as e:
            self.warnings.append(f"Could not validate API integration: {e}")
        
        # Check for mock data in lead storage
        try:
            from app_api import _memory_leads
            for lead in _memory_leads:
                if 'sample' in str(lead.get('id', '')).lower() or 'mock' in str(lead.get('source', '')).lower():
                    mock_indicators.append("Sample/mock leads found in storage")
                    break
        except Exception as e:
            self.warnings.append(f"Could not validate lead storage: {e}")
        
        if mock_indicators:
            self.errors.extend(mock_indicators)
            return False
        
        return True
    
    def validate_production_readiness(self):
        """Run all production validation checks"""
        logger.info("🚀 CRYSTAL BAY TRAVEL - Production Deployment Validation")
        logger.info("=" * 60)
        
        env_valid = self.validate_environment()
        samo_valid = self.validate_samo_configuration()
        data_valid = self.validate_data_sources()
        
        # Display results
        if self.errors:
            logger.error("❌ Production deployment blocked:")
            for error in self.errors:
                logger.error(f"   • {error}")
        
        if self.warnings:
            logger.warning("⚠️ Production deployment warnings:")
            for warning in self.warnings:
                logger.warning(f"   • {warning}")
        
        is_ready = env_valid and samo_valid and data_valid
        
        if is_ready:
            logger.info("✅ System validated for production deployment")
            logger.info("📍 Expected production IP: 34.117.33.233")
            logger.info("🔗 SAMO API endpoint: https://booking-kz.crystalbay.com/export/default.php")
        else:
            logger.error("❌ System NOT ready for production deployment")
        
        return is_ready
    
    def get_deployment_summary(self):
        """Get summary of deployment status"""
        return {
            'ready': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'required_ip': '34.117.33.233',
            'samo_endpoint': 'https://booking-kz.crystalbay.com/export/default.php',
            'oauth_token': '27bd59a7ac67422189789f0188167379'
        }

def validate_production_deployment():
    """Main validation function for production deployment"""
    validator = ProductionValidator()
    is_ready = validator.validate_production_readiness()
    
    summary = validator.get_deployment_summary()
    
    return is_ready, summary

if __name__ == '__main__':
    is_ready, summary = validate_production_deployment()
    
    if is_ready:
        print("\n🎯 PRODUCTION DEPLOYMENT READY")
        print("System configured for Crystal Bay Travel production environment")
        sys.exit(0)
    else:
        print("\n❌ PRODUCTION DEPLOYMENT BLOCKED")
        print("Resolve errors above before deployment")
        sys.exit(1)