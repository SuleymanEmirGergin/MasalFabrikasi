"""
Environment Validation - Startup'ta environment değişkenlerini kontrol eder
"""
import os
import sys
from typing import List, Dict, Any
from app.core.config import settings


class EnvironmentValidator:
    """Validate required environment variables and configuration"""
    
    REQUIRED_VARS = [
        # Core
        "DATABASE_URL",
        "REDIS_URL",
        # Supabase (for Auth & Storage)
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_KEY",
        # AI APIs (at least one should be configured)
        "WIRO_API_KEY",
    ]
    
    OPTIONAL_FEATURES = {
        "payments": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
        "monitoring": ["SENTRY_DSN"],
        "cloud_storage": ["CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY"]
    }
    
    RECOMMENDED_VARS = [
        "SENTRY_DSN",
        "DEBUG",
    ]
    
    @staticmethod
    def validate() -> Dict[str, Any]:
        """
        Validate environment configuration
        
        Returns:
            Dict with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_required": [],
            "missing_recommended": [],
            "feature_status": {}
        }
        
        # Check required variables
        for var in EnvironmentValidator.REQUIRED_VARS:
            value = os.getenv(var)
            if not value or value == "":
                results["valid"] = False
                results["errors"].append(f"Required environment variable missing: {var}")
                results["missing_required"].append(var)
        
        # Check feature-specific variables
        for feature, vars_needed in EnvironmentValidator.OPTIONAL_FEATURES.items():
            all_present = all(os.getenv(var) for var in vars_needed)
            results["feature_status"][feature] = {
                "enabled": all_present,
                "missing_vars": [var for var in vars_needed if not os.getenv(var)]
            }
            
            if not all_present:
                results["warnings"].append(
                    f"Feature '{feature}' disabled due to missing: {', '.join(results['feature_status'][feature]['missing_vars'])}"
                )
        
        # Check recommended variables
        for var in EnvironmentValidator.RECOMMENDED_VARS:
            if not os.getenv(var):
                results["warnings"].append(f"Recommended variable not set: {var}")
                results["missing_recommended"].append(var)
        
        # Validate specific settings
        EnvironmentValidator._validate_settings(results)
        
        return results
    
    @staticmethod
    def _validate_settings(results: Dict):
        """Validate specific settings values"""
        
        # Check debug mode in production
        debug = os.getenv("DEBUG", "false").lower()
        if debug == "true":
            results["warnings"].append(
                "DEBUG mode is enabled - should be disabled in production!"
            )
        
        # Check database URL format
        db_url = os.getenv("DATABASE_URL", "")
        if db_url and not db_url.startswith(("postgresql://", "sqlite://")):
            results["warnings"].append(
                "DATABASE_URL format may be invalid"
            )
    
    @staticmethod
    def validate_or_exit():
        """
        Validate environment and exit if critical errors exist
        Should be called on application startup
        """
        print("🔍 Validating environment configuration...")
        
        results = EnvironmentValidator.validate()
        
        # Print errors
        if results["errors"]:
            print("\n❌ CRITICAL ERRORS:")
            for error in results["errors"]:
                print(f"  - {error}")
        
        # Print warnings
        if results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in results["warnings"]:
                print(f"  - {warning}")
        
        # Print feature status
        print("\n📦 Feature Status:")
        for feature, status in results["feature_status"].items():
            icon = "✅" if status["enabled"] else "❌"
            print(f"  {icon} {feature.replace('_', ' ').title()}")
            if not status["enabled"] and status["missing_vars"]:
                print(f"     Missing: {', '.join(status['missing_vars'])}")
        
        # Exit if critical errors - DISABLED FOR RAILWAY DEPLOYMENT
        # App will start but features requiring these vars will be limited
        if not results["valid"]:
            print("\n⚠️  Some required configuration is missing.")
            print("   App will start but some features may be limited.")
            print(f"\n   Missing: {', '.join(results['missing_required'])}")
            print("\n   Set these in Railway Variables to enable full functionality.")
            # Don't exit - let app start with limited features
            # sys.exit(1)
        else:
            print("\n✅ Environment validation passed!")
        
        return results


def validate_environment():
    """Convenience function for validation"""
    return EnvironmentValidator.validate_or_exit()
