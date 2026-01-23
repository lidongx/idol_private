"""
AppleIAPService - Service for managing Apple In-App Purchase integration
Story 7.3: Apple IAP集成
"""
from typing import Dict, Optional, List
from datetime import datetime
import httpx
import logging
import base64
import json

from app.config import settings

logger = logging.getLogger(__name__)


class AppleIAPService:
    """Service for managing Apple In-App Purchase receipt verification"""

    # Apple receipt status codes
    STATUS_VALID = 0
    STATUS_SANDBOX_RECEIPT_TO_PRODUCTION = 21007
    STATUS_PRODUCTION_RECEIPT_TO_SANDBOX = 21008

    def __init__(self):
        self.sandbox_mode = settings.APPLE_SANDBOX_MODE
        self.shared_secret = settings.APPLE_SHARED_SECRET

    async def verify_receipt(
        self,
        receipt_data: str,
        exclude_old_transactions: bool = True
    ) -> Optional[Dict]:
        """
        Verify Apple receipt with App Store

        Args:
            receipt_data: Base64 encoded receipt data from iOS
            exclude_old_transactions: Whether to exclude old transactions (recommended)

        Returns:
            Verification result dictionary or None if verification fails

        Apple Response Format:
        {
            "status": 0,
            "environment": "Sandbox",
            "receipt": {...},
            "latest_receipt_info": [...],
            "pending_renewal_info": [...]
        }
        """
        try:
            # Determine verification URL based on mode
            if self.sandbox_mode:
                verify_url = settings.APPLE_VERIFY_URL_SANDBOX
            else:
                verify_url = settings.APPLE_VERIFY_URL_PRODUCTION

            # Prepare request payload
            payload = {
                "receipt-data": receipt_data,
                "password": self.shared_secret,
                "exclude-old-transactions": exclude_old_transactions
            }

            # Send verification request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(verify_url, json=payload)
                result = response.json()

            status = result.get('status')

            # Handle sandbox/production mismatch
            if status == self.STATUS_SANDBOX_RECEIPT_TO_PRODUCTION:
                # Production receipt sent to sandbox, retry with production
                logger.info("[Apple IAP] Retrying with production environment")
                return await self._verify_with_production(receipt_data, exclude_old_transactions)

            elif status == self.STATUS_PRODUCTION_RECEIPT_TO_SANDBOX:
                # Sandbox receipt sent to production, retry with sandbox
                logger.info("[Apple IAP] Retrying with sandbox environment")
                return await self._verify_with_sandbox(receipt_data, exclude_old_transactions)

            elif status == self.STATUS_VALID:
                # Receipt is valid
                logger.info("[Apple IAP] Receipt verified successfully")
                return result

            else:
                # Other error
                logger.error(f"[Apple IAP] Receipt verification failed: status={status}")
                return None

        except httpx.TimeoutException as e:
            logger.error(f"[Apple IAP] Verification timeout: {e}")
            return None
        except Exception as e:
            logger.error(f"[Apple IAP] Error verifying receipt: {e}")
            return None

    async def _verify_with_production(
        self,
        receipt_data: str,
        exclude_old_transactions: bool
    ) -> Optional[Dict]:
        """Verify receipt with production endpoint"""
        try:
            payload = {
                "receipt-data": receipt_data,
                "password": self.shared_secret,
                "exclude-old-transactions": exclude_old_transactions
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.APPLE_VERIFY_URL_PRODUCTION,
                    json=payload
                )
                result = response.json()

            if result.get('status') == self.STATUS_VALID:
                return result
            else:
                return None

        except Exception as e:
            logger.error(f"[Apple IAP] Error in production verification: {e}")
            return None

    async def _verify_with_sandbox(
        self,
        receipt_data: str,
        exclude_old_transactions: bool
    ) -> Optional[Dict]:
        """Verify receipt with sandbox endpoint"""
        try:
            payload = {
                "receipt-data": receipt_data,
                "password": self.shared_secret,
                "exclude-old-transactions": exclude_old_transactions
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    settings.APPLE_VERIFY_URL_SANDBOX,
                    json=payload
                )
                result = response.json()

            if result.get('status') == self.STATUS_VALID:
                return result
            else:
                return None

        except Exception as e:
            logger.error(f"[Apple IAP] Error in sandbox verification: {e}")
            return None

    def extract_subscription_info(self, verification_result: Dict) -> Optional[Dict]:
        """
        Extract subscription information from verification result

        Args:
            verification_result: Result from verify_receipt()

        Returns:
            Dictionary with subscription details or None
        """
        try:
            # Get latest receipt info (most recent transaction)
            latest_receipt_info = verification_result.get('latest_receipt_info', [])

            if not latest_receipt_info:
                logger.warning("[Apple IAP] No latest_receipt_info found")
                return None

            # Get the most recent transaction
            latest_transaction = latest_receipt_info[-1]

            # Extract subscription details
            product_id = latest_transaction.get('product_id')
            transaction_id = latest_transaction.get('transaction_id')
            original_transaction_id = latest_transaction.get('original_transaction_id')
            purchase_date_ms = latest_transaction.get('purchase_date_ms')
            expires_date_ms = latest_transaction.get('expires_date_ms')
            is_trial_period = latest_transaction.get('is_trial_period') == 'true'
            is_in_intro_offer_period = latest_transaction.get('is_in_intro_offer_period') == 'true'

            # Check if subscription is still active
            is_active = False
            if expires_date_ms:
                expires_date = datetime.fromtimestamp(int(expires_date_ms) / 1000)
                is_active = expires_date > datetime.utcnow()

            # Get pending renewal info
            pending_renewal_info = verification_result.get('pending_renewal_info', [])
            auto_renew_status = False
            if pending_renewal_info:
                auto_renew_status = pending_renewal_info[0].get('auto_renew_status') == '1'

            return {
                'product_id': product_id,
                'transaction_id': transaction_id,
                'original_transaction_id': original_transaction_id,
                'purchase_date': datetime.fromtimestamp(int(purchase_date_ms) / 1000) if purchase_date_ms else None,
                'expires_date': datetime.fromtimestamp(int(expires_date_ms) / 1000) if expires_date_ms else None,
                'is_trial_period': is_trial_period,
                'is_in_intro_offer_period': is_in_intro_offer_period,
                'is_active': is_active,
                'auto_renew_status': auto_renew_status
            }

        except Exception as e:
            logger.error(f"[Apple IAP] Error extracting subscription info: {e}")
            return None

    def get_plan_type_from_product_id(self, product_id: str) -> Optional[str]:
        """
        Map Apple product ID to subscription plan type

        Args:
            product_id: Apple product ID (e.g., com.idol.premium.monthly)

        Returns:
            Plan type string ('monthly' or 'yearly') or None
        """
        if product_id == settings.APPLE_PRODUCT_ID_MONTHLY:
            return 'monthly'
        elif product_id == settings.APPLE_PRODUCT_ID_YEARLY:
            return 'yearly'
        else:
            logger.warning(f"[Apple IAP] Unknown product ID: {product_id}")
            return None

    def parse_server_notification(self, notification_data: Dict) -> Optional[Dict]:
        """
        Parse Apple Server-to-Server notification

        Args:
            notification_data: Notification payload from Apple

        Returns:
            Parsed notification data or None

        Notification Types:
        - INITIAL_BUY: First-time subscription
        - DID_RENEW: Subscription renewed
        - DID_CHANGE_RENEWAL_PREF: User changed renewal preference
        - DID_CHANGE_RENEWAL_STATUS: Auto-renew status changed
        - DID_FAIL_TO_RENEW: Renewal failed
        - CANCEL: Subscription cancelled
        - REFUND: Subscription refunded
        """
        try:
            notification_type = notification_data.get('notification_type')
            auto_renew_status = notification_data.get('auto_renew_status')
            auto_renew_status_change_date = notification_data.get('auto_renew_status_change_date_ms')

            # Get unified receipt
            unified_receipt = notification_data.get('unified_receipt', {})
            latest_receipt_info = unified_receipt.get('latest_receipt_info', [])

            if not latest_receipt_info:
                logger.warning("[Apple IAP] No latest_receipt_info in notification")
                return None

            latest_transaction = latest_receipt_info[-1]

            return {
                'notification_type': notification_type,
                'auto_renew_status': auto_renew_status == 'true',
                'product_id': latest_transaction.get('product_id'),
                'transaction_id': latest_transaction.get('transaction_id'),
                'original_transaction_id': latest_transaction.get('original_transaction_id'),
                'expires_date_ms': latest_transaction.get('expires_date_ms'),
                'purchase_date_ms': latest_transaction.get('purchase_date_ms')
            }

        except Exception as e:
            logger.error(f"[Apple IAP] Error parsing server notification: {e}")
            return None

    def validate_bundle_id(self, verification_result: Dict) -> bool:
        """
        Validate that receipt bundle ID matches app bundle ID

        Args:
            verification_result: Result from verify_receipt()

        Returns:
            True if bundle ID matches, False otherwise
        """
        try:
            receipt = verification_result.get('receipt', {})
            bundle_id = receipt.get('bundle_id')

            if bundle_id == settings.APPLE_BUNDLE_ID:
                return True
            else:
                logger.warning(f"[Apple IAP] Bundle ID mismatch: {bundle_id} != {settings.APPLE_BUNDLE_ID}")
                return False

        except Exception as e:
            logger.error(f"[Apple IAP] Error validating bundle ID: {e}")
            return False
