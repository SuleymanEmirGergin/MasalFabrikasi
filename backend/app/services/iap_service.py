"""
In-App Purchase (IAP) Receipt Validation Service
Validates purchases from Apple App Store and Google Play Store
"""

import httpx
import os
import logging
from typing import Dict, Optional
import base64
import json

logger = logging.getLogger(__name__)

class IAPService:
    """
    In-App Purchase validation service.
    """
    
    # Sandbox vs Production
    APPLE_SANDBOX_URL = "https://sandbox.itunes.apple.com/verifyReceipt"
    APPLE_PRODUCTION_URL = "https://buy.itunes.apple.com/verifyReceipt"
    GOOGLE_PLAY_URL = "https://www.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/products/{product_id}/tokens/{token}"
    
    @staticmethod
    async def validate_apple_receipt(receipt_data: str, is_sandbox: bool = False) -> Optional[Dict]:
        """
        Validate Apple App Store receipt.
        
        Args:
            receipt_data: Base64 encoded receipt
            is_sandbox: Use sandbox environment
            
        Returns:
            Validated receipt data or None
        """
        url = IAPService.APPLE_SANDBOX_URL if is_sandbox else IAPService.APPLE_PRODUCTION_URL
        
        payload = {
            "receipt-data": receipt_data,
            "password": os.getenv("APPLE_SHARED_SECRET"),  # From App Store Connect
            "exclude-old-transactions": True
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10.0)
                data = response.json()
                
                # Check status
                status = data.get("status")
                
                if status == 0:
                    # Valid receipt
                    logger.info("Apple receipt validated successfully")
                    return {
                        "platform": "ios",
                        "product_id": data["receipt"]["product_id"],
                        "transaction_id": data["receipt"]["transaction_id"],
                        "purchase_date": data["receipt"]["purchase_date"],
                        "is_valid": True
                    }
                
                elif status == 21007:
                    # Sandbox receipt sent to production
                    logger.info("Retrying with sandbox URL")
                    return await IAPService.validate_apple_receipt(receipt_data, is_sandbox=True)
                
                else:
                    logger.error(f"Apple receipt validation failed: status {status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Apple validation error: {e}")
            return None
    
    @staticmethod
    async def validate_google_receipt(
        package_name: str,
        product_id: str,
        purchase_token: str
    ) -> Optional[Dict]:
        """
        Validate Google Play Store receipt.
        
        Args:
            package_name: App package name
            product_id: Product/SKU ID
            purchase_token: Purchase token from Google
            
        Returns:
            Validated receipt data or None
        """
        # This requires Google Service Account credentials
        # and Google Play Developer API enabled
        
        try:
            # Load service account credentials
            credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if not credentials_json:
                logger.error("Google Service Account credentials not found")
                return None
            
            credentials = json.loads(credentials_json)
            
            # Get access token (simplified - use google-auth library in production)
            # For now, just a placeholder
            
            url = IAPService.GOOGLE_PLAY_URL.format(
                package_name=package_name,
                product_id=product_id,
                token=purchase_token
            )
            
            # In production, use proper OAuth2 authentication
            # This is a simplified version
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {os.getenv('GOOGLE_ACCESS_TOKEN')}"
                }
                response = await client.get(url, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if purchase is valid
                    purchase_state = data.get("purchaseState")
                    
                    if purchase_state == 0:  # Purchased
                        logger.info("Google receipt validated successfully")
                        return {
                            "platform": "android",
                            "product_id": product_id,
                            "purchase_token": purchase_token,
                            "purchase_time": data.get("purchaseTimeMillis"),
                            "is_valid": True
                        }
                    else:
                        logger.error(f"Google purchase state invalid: {purchase_state}")
                        return None
                else:
                    logger.error(f"Google validation failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Google validation error: {e}")
            return None
    
    @staticmethod
    def get_product_credits(product_id: str) -> int:
        """Get credits for a product."""
        products = {
            "credits_100": 100,
            "credits_500": 500,
            "credits_1000": 1000,
            "premium_monthly": 0,
            "premium_yearly": 0,
        }
        return products.get(product_id, 0)
    
    @staticmethod
    def is_premium_product(product_id: str) -> bool:
        """Check if product is premium subscription."""
        return "premium" in product_id.lower()

# Export
iap_service = IAPService()
