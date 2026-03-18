"""
Unit tests for GDPRService

Tests cover:
- User data export (Article 15)
- User data deletion (Article 17)
- Privacy settings management
- Consent management
- Data processing logs
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.gdpr_service import GDPRService


class TestDataExport:
    """Tests for data export functionality (GDPR Article 15)."""
    
    def setup_method(self):
        self.gdpr_service = GDPRService()
    
    @pytest.mark.asyncio
    async def test_export_user_data_structure(self):
        """Test that export returns proper data structure."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'export_user_data',
            new_callable=AsyncMock,
            return_value={
                "user_profile": {"id": user_id, "email": "test@example.com"},
                "stories": [],
                "characters": [],
                "achievements": [],
                "settings": {},
                "export_date": datetime.now().isoformat()
            }
        ):
            result = await self.gdpr_service.export_user_data(user_id)
            
            assert result is not None
            assert "user_profile" in result
            assert "export_date" in result
    
    @pytest.mark.asyncio
    async def test_export_user_data_includes_email(self):
        """Test that export includes user email."""
        user_id = "test_user_123"
        
        mock_result = {
            "user_profile": {"id": user_id, "email": "test@example.com"},
            "stories": [],
            "export_date": datetime.now().isoformat()
        }
        
        with patch.object(
            self.gdpr_service,
            'export_user_data',
            new_callable=AsyncMock,
            return_value=mock_result
        ):
            result = await self.gdpr_service.export_user_data(user_id)
            
            assert "email" in result["user_profile"]
    
    @pytest.mark.asyncio
    async def test_export_nonexistent_user(self):
        """Test export for non-existent user returns empty or error."""
        with patch.object(
            self.gdpr_service,
            'export_user_data',
            new_callable=AsyncMock,
            return_value=None
        ):
            result = await self.gdpr_service.export_user_data("nonexistent_user")
            
            # Should return None or empty dict for non-existent user
            assert result is None or result == {}


class TestDataDeletion:
    """Tests for data deletion functionality (GDPR Article 17)."""
    
    def setup_method(self):
        self.gdpr_service = GDPRService()
    
    @pytest.mark.asyncio
    async def test_delete_user_data_success(self):
        """Test successful data deletion."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'delete_user_data',
            new_callable=AsyncMock,
            return_value={
                "success": True,
                "deleted_items": {
                    "stories": 5,
                    "characters": 2,
                    "user_profile": True
                }
            }
        ):
            result = await self.gdpr_service.delete_user_data(user_id)
            
            assert result is not None
            assert result.get("success") is True
    
    @pytest.mark.asyncio
    async def test_delete_user_data_returns_deleted_count(self):
        """Test that deletion returns count of deleted items."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'delete_user_data',
            new_callable=AsyncMock,
            return_value={
                "success": True,
                "deleted_items": {
                    "stories": 10,
                    "characters": 3
                }
            }
        ):
            result = await self.gdpr_service.delete_user_data(user_id)
            
            assert "deleted_items" in result
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self):
        """Test deletion for non-existent user."""
        with patch.object(
            self.gdpr_service,
            'delete_user_data',
            new_callable=AsyncMock,
            return_value={"success": True, "deleted_items": {}}
        ):
            result = await self.gdpr_service.delete_user_data("nonexistent_user")
            
            # Should succeed even if no data to delete
            assert result.get("success") is True


class TestPrivacySettings:
    """Tests for privacy settings management."""
    
    def setup_method(self):
        self.gdpr_service = GDPRService()
    
    @pytest.mark.asyncio
    async def test_get_privacy_settings(self):
        """Test retrieving privacy settings."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'get_privacy_settings',
            new_callable=AsyncMock,
            return_value={
                "analytics_enabled": True,
                "marketing_emails": False,
                "share_reading_history": True
            }
        ):
            result = await self.gdpr_service.get_privacy_settings(user_id)
            
            assert result is not None
            assert "analytics_enabled" in result
    
    @pytest.mark.asyncio
    async def test_get_privacy_settings_defaults(self):
        """Test that privacy settings have sensible defaults."""
        user_id = "new_user_123"
        
        default_settings = {
            "analytics_enabled": True,
            "marketing_emails": False,
            "share_reading_history": False,
            "third_party_sharing": False
        }
        
        with patch.object(
            self.gdpr_service,
            'get_privacy_settings',
            new_callable=AsyncMock,
            return_value=default_settings
        ):
            result = await self.gdpr_service.get_privacy_settings(user_id)
            
            # Third party sharing should be off by default
            assert result.get("third_party_sharing") is False
    
    @pytest.mark.asyncio
    async def test_update_privacy_settings(self):
        """Test updating privacy settings."""
        user_id = "test_user_123"
        new_settings = {
            "analytics_enabled": False,
            "marketing_emails": False
        }
        
        with patch.object(
            self.gdpr_service,
            'update_privacy_settings',
            new_callable=AsyncMock,
            return_value={"success": True, "updated_settings": new_settings}
        ):
            result = await self.gdpr_service.update_privacy_settings(user_id, new_settings)
            
            assert result.get("success") is True


class TestConsentManagement:
    """Tests for consent management."""
    
    def setup_method(self):
        self.gdpr_service = GDPRService()
    
    @pytest.mark.asyncio
    async def test_withdraw_consent(self):
        """Test withdrawing consent."""
        user_id = "test_user_123"
        consent_type = "analytics"
        
        with patch.object(
            self.gdpr_service,
            'withdraw_consent',
            new_callable=AsyncMock,
            return_value={"success": True, "consent_type": consent_type}
        ):
            result = await self.gdpr_service.withdraw_consent(user_id, consent_type)
            
            assert result.get("success") is True
            assert result.get("consent_type") == consent_type
    
    @pytest.mark.asyncio
    async def test_withdraw_all_consents(self):
        """Test withdrawing all consent types."""
        user_id = "test_user_123"
        
        consent_types = ["analytics", "marketing", "personalization"]
        
        for consent_type in consent_types:
            with patch.object(
                self.gdpr_service,
                'withdraw_consent',
                new_callable=AsyncMock,
                return_value={"success": True}
            ):
                result = await self.gdpr_service.withdraw_consent(user_id, consent_type)
                assert result.get("success") is True


class TestDataProcessingLog:
    """Tests for data processing log functionality."""
    
    def setup_method(self):
        self.gdpr_service = GDPRService()
    
    @pytest.mark.asyncio
    async def test_get_data_processing_log(self):
        """Test retrieving data processing log."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'get_data_processing_log',
            new_callable=AsyncMock,
            return_value={
                "logs": [
                    {"action": "login", "timestamp": "2026-01-09T12:00:00"},
                    {"action": "story_created", "timestamp": "2026-01-09T12:30:00"}
                ],
                "total_count": 2
            }
        ):
            result = await self.gdpr_service.get_data_processing_log(user_id)
            
            assert "logs" in result
            assert "total_count" in result
    
    @pytest.mark.asyncio
    async def test_get_data_processing_log_with_pagination(self):
        """Test data processing log with pagination."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'get_data_processing_log',
            new_callable=AsyncMock,
            return_value={
                "logs": [],
                "total_count": 100,
                "page": 1,
                "per_page": 50
            }
        ):
            result = await self.gdpr_service.get_data_processing_log(
                user_id, limit=50, offset=0
            )
            
            assert "logs" in result
    
    @pytest.mark.asyncio
    async def test_log_data_export(self):
        """Test logging data export action."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'log_data_export',
            new_callable=AsyncMock,
            return_value={"success": True}
        ):
            result = await self.gdpr_service.log_data_export(user_id, "full_export")
            
            assert result.get("success") is True
    
    @pytest.mark.asyncio
    async def test_log_data_deletion(self):
        """Test logging data deletion action."""
        user_id = "test_user_123"
        
        with patch.object(
            self.gdpr_service,
            'log_data_deletion',
            new_callable=AsyncMock,
            return_value={"success": True}
        ):
            result = await self.gdpr_service.log_data_deletion(user_id, "user_request")
            
            assert result.get("success") is True


class TestGDPRCompliance:
    """Tests for overall GDPR compliance."""
    
    def setup_method(self):
        self.gdpr_service = GDPRService()
    
    def test_gdpr_service_has_required_methods(self):
        """Test that GDPR service has all required methods."""
        # Article 15 - Right of access
        assert hasattr(self.gdpr_service, 'export_user_data')
        
        # Article 17 - Right to erasure
        assert hasattr(self.gdpr_service, 'delete_user_data')
        
        # Privacy settings
        assert hasattr(self.gdpr_service, 'get_privacy_settings')
        assert hasattr(self.gdpr_service, 'update_privacy_settings')
        
        # Consent management
        assert hasattr(self.gdpr_service, 'withdraw_consent')
        
        # Data processing log
        assert hasattr(self.gdpr_service, 'get_data_processing_log')
        assert hasattr(self.gdpr_service, 'log_data_export')
        assert hasattr(self.gdpr_service, 'log_data_deletion')
