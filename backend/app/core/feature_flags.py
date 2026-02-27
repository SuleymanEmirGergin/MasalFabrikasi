"""
Feature Flags Service - Enable/disable features dynamically
"""
from typing import Dict, Any, Optional
from enum import Enum
import json
import os


class FeatureFlag(str, Enum):
    """Feature flag definitions"""
    VOICE_CLONING = "voice_cloning"
    MAGIC_CANVAS = "magic_canvas"
    CHARACTER_CHAT = "character_chat"
    BEDTIME_MODE = "bedtime_mode"
    SEMANTIC_SEARCH = "semantic_search"
    ADVANCED_ANALYTICS = "advanced_analytics"
    PREMIUM_FEATURES = "premium_features"
    EXPERIMENTAL_AI = "experimental_ai"
    MAINTENANCE_MODE = "maintenance_mode"


class FeatureFlagService:
    """
    Feature flag management
    
    Supports:
    - Environment variables
    - JSON config file
    - User/role based flags
    - Percentage rollout
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv("FEATURE_FLAGS_FILE", "feature_flags.json")
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, Any]:
        """Load feature flags from file or defaults"""
        
        # Default flags (all enabled)
        defaults = {
            FeatureFlag.VOICE_CLONING: {
                "enabled": True,
                "description": "Voice cloning with ElevenLabs",
                "requires_key": "ELEVENLABS_API_KEY"
            },
            FeatureFlag.MAGIC_CANVAS: {
                "enabled": True,
                "description": "AI drawing tool"
            },
            FeatureFlag.CHARACTER_CHAT: {
                "enabled": True,
                "description": "Chat with story characters"
            },
            FeatureFlag.BEDTIME_MODE: {
                "enabled": True,
                "description": "Bedtime story mode"
            },
            FeatureFlag.SEMANTIC_SEARCH: {
                "enabled": True,
                "description": "Vector-based semantic search",
                "requires_key": "OPENAI_API_KEY"
            },
            FeatureFlag.ADVANCED_ANALYTICS: {
                "enabled": True,
                "description": "Advanced reading analytics"
            },
            FeatureFlag.PREMIUM_FEATURES: {
                "enabled": True,
                "description": "Premium subscription features",
                "roles": ["premium", "pro"]
            },
            FeatureFlag.EXPERIMENTAL_AI: {
                "enabled": False,
                "description": "Experimental AI features",
                "rollout_percentage": 10  # Only 10% of users
            },
            FeatureFlag.MAINTENANCE_MODE: {
                "enabled": False,
                "description": "Maintenance mode - API read-only"
            }
        }
        
        # Try to load from file
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_flags = json.load(f)
                    # Merge with defaults
                    defaults.update(file_flags)
        except Exception as e:
            print(f"Failed to load feature flags from file: {e}")
        
        # Override with environment variables
        for flag in FeatureFlag:
            env_var = f"FEATURE_{flag.value.upper()}"
            env_value = os.getenv(env_var)
            if env_value is not None:
                defaults[flag] = {
                    **defaults.get(flag, {}),
                    "enabled": env_value.lower() == "true"
                }
        
        return defaults
    
    def is_enabled(
        self,
        feature: FeatureFlag,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> bool:
        """
        Check if a feature is enabled
        
        Args:
            feature: Feature flag to check
            user_id: Optional user ID for percentage rollout
            user_role: Optional user role for role-based features
        
        Returns:
            True if feature is enabled
        """
        flag_config = self.flags.get(feature, {})
        
        # Check if globally enabled
        if not flag_config.get("enabled", False):
            return False
        
        # Check if required API key exists
        if "requires_key" in flag_config:
            if not os.getenv(flag_config["requires_key"]):
                return False
        
        # Check role-based access
        if "roles" in flag_config:
            if not user_role or user_role not in flag_config["roles"]:
                return False
        
        # Check percentage rollout
        if "rollout_percentage" in flag_config and user_id:
            percentage = flag_config["rollout_percentage"]
            # Simple hash-based percentage
            user_hash = hash(user_id) % 100
            if user_hash >= percentage:
                return False
        
        return True
    
    def get_all_flags(self, user_role: Optional[str] = None) -> Dict[str, bool]:
        """
        Get status of all flags
        
        Returns:
            Dict of flag name -> enabled status
        """
        return {
            flag.value: self.is_enabled(flag, user_role=user_role)
            for flag in FeatureFlag
        }
    
    def get_flag_info(self, feature: FeatureFlag) -> Dict[str, Any]:
        """Get detailed info about a feature flag"""
        return self.flags.get(feature, {})


# Global instance
feature_flags = FeatureFlagService()


# Convenience functions
def is_feature_enabled(feature: FeatureFlag, user_id: str = None, user_role: str = None) -> bool:
    """Check if feature is enabled"""
    return feature_flags.is_enabled(feature, user_id, user_role)


def require_feature(feature: FeatureFlag):
    """
    Decorator to require a feature flag
    
    Usage:
        @require_feature(FeatureFlag.VOICE_CLONING)
        async def clone_voice():
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            from app.core.exceptions import AuthorizationError
            
            if not is_feature_enabled(feature):
                raise AuthorizationError(f"Feature '{feature.value}' is not enabled")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
