"""
PaymentService - Service for managing Alipay, WeChat Pay, Apple IAP, and Google Play Billing
Story 7.2: 支付宝与微信支付集成
Story 7.3: Apple In-App Purchase集成
Story 7.4: Google Play Billing集成
"""
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime
from alipay import AliPay
from wechatpy.pay import WeChatPay
from wechatpy.exceptions import WeChatPayException
import logging
import httpx
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from app.config import settings
from app.models.order import Order

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing payments via Alipay, WeChat Pay, Apple IAP, and Google Play Billing"""

    def __init__(self):
        self._alipay_client = None
        self._wechat_client = None
        self._google_play_client = None

    @property
    def alipay(self) -> AliPay:
        """
        Get or create Alipay client instance

        Returns:
            AliPay client instance
        """
        if self._alipay_client is None:
            # Check if keys are file paths or direct strings
            app_private_key = self._load_key_or_string(settings.ALIPAY_PRIVATE_KEY)
            alipay_public_key = self._load_key_or_string(settings.ALIPAY_PUBLIC_KEY)

            self._alipay_client = AliPay(
                appid=settings.ALIPAY_APPID,
                app_private_key_string=app_private_key,
                alipay_public_key_string=alipay_public_key,
                sign_type=settings.ALIPAY_SIGN_TYPE,
                debug=settings.ALIPAY_DEBUG
            )

        return self._alipay_client

    @property
    def wechat(self) -> WeChatPay:
        """
        Get or create WeChat Pay client instance

        Returns:
            WeChatPay client instance
        """
        if self._wechat_client is None:
            self._wechat_client = WeChatPay(
                appid=settings.WECHAT_APPID,
                mch_id=settings.WECHAT_MCH_ID,
                api_key=settings.WECHAT_API_KEY,
                mch_cert=settings.WECHAT_APICLIENT_CERT,
                mch_key=settings.WECHAT_APICLIENT_KEY
            )

        return self._wechat_client

    def _load_key_or_string(self, key_value: str) -> str:
        """
        Load key from file or return as string

        Args:
            key_value: Key file path or key string

        Returns:
            Key string
        """
        if not key_value:
            return ""

        # If it looks like a file path
        if key_value.endswith('.pem') or key_value.endswith('.txt'):
            try:
                with open(key_value, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                logger.warning(f"Key file not found: {key_value}")
                return key_value
        else:
            return key_value

    def create_alipay_payment(self, order: Order) -> Dict:
        """
        Create Alipay payment for an order

        Args:
            order: Order object

        Returns:
            Dictionary with payment_url and order details

        Raises:
            ValueError: If order is invalid or payment creation fails
        """
        if not order:
            raise ValueError("Order is required")

        if order.status != Order.STATUS_PENDING:
            raise ValueError(f"Order {order.order_no} is not in pending status")

        try:
            # Create Alipay payment
            order_string = self.alipay.api_alipay_trade_page_pay(
                out_trade_no=order.order_no,
                total_amount=str(float(order.amount)),
                subject=f"{order.plan.plan_name} - idol_private订阅",
                return_url=settings.ALIPAY_RETURN_URL,
                notify_url=settings.ALIPAY_NOTIFY_URL,
                product_code="FAST_INSTANT_TRADE_PAY"
            )

            # Construct payment URL
            if settings.ALIPAY_DEBUG:
                # Sandbox environment
                payment_url = f"https://openapi.alipaydev.com/gateway.do?{order_string}"
            else:
                # Production environment
                payment_url = f"https://openapi.alipay.com/gateway.do?{order_string}"

            logger.info(f"[Alipay] Created payment for order {order.order_no}")

            return {
                'payment_method': 'alipay',
                'order_no': order.order_no,
                'payment_url': payment_url,
                'amount': float(order.amount)
            }

        except Exception as e:
            logger.error(f"[Alipay] Error creating payment: {e}")
            raise ValueError(f"Failed to create Alipay payment: {str(e)}")

    def create_wechat_payment(self, order: Order) -> Dict:
        """
        Create WeChat Pay Native (QR code) payment for an order

        Args:
            order: Order object

        Returns:
            Dictionary with code_url (QR code URL) and order details

        Raises:
            ValueError: If order is invalid or payment creation fails
        """
        if not order:
            raise ValueError("Order is required")

        if order.status != Order.STATUS_PENDING:
            raise ValueError(f"Order {order.order_no} is not in pending status")

        try:
            # Create WeChat Pay Native order
            result = self.wechat.order.create(
                trade_type='NATIVE',
                out_trade_no=order.order_no,
                total_fee=int(float(order.amount) * 100),  # Convert to cents
                body=f"{order.plan.plan_name} - idol_private订阅",
                notify_url=settings.WECHAT_NOTIFY_URL
            )

            if result.get('return_code') != 'SUCCESS' or result.get('result_code') != 'SUCCESS':
                error_msg = result.get('err_code_des', 'Unknown error')
                raise ValueError(f"WeChat Pay error: {error_msg}")

            logger.info(f"[WeChat Pay] Created payment for order {order.order_no}")

            return {
                'payment_method': 'wechat',
                'order_no': order.order_no,
                'code_url': result.get('code_url'),  # QR code URL
                'prepay_id': result.get('prepay_id'),
                'amount': float(order.amount)
            }

        except WeChatPayException as e:
            logger.error(f"[WeChat Pay] Error creating payment: {e}")
            raise ValueError(f"Failed to create WeChat payment: {str(e)}")
        except Exception as e:
            logger.error(f"[WeChat Pay] Unexpected error: {e}")
            raise ValueError(f"Failed to create WeChat payment: {str(e)}")

    def verify_alipay_callback(self, data: dict, signature: str) -> bool:
        """
        Verify Alipay payment callback signature

        Args:
            data: Callback data from Alipay
            signature: Signature from Alipay

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Remove sign from data before verification
            data_copy = data.copy()
            if 'sign' in data_copy:
                del data_copy['sign']
            if 'sign_type' in data_copy:
                del data_copy['sign_type']

            return self.alipay.verify(data_copy, signature)

        except Exception as e:
            logger.error(f"[Alipay] Error verifying callback: {e}")
            return False

    def verify_wechat_callback(self, xml_data: str) -> Optional[Dict]:
        """
        Verify and parse WeChat Pay callback

        Args:
            xml_data: XML data from WeChat Pay callback

        Returns:
            Parsed callback data if valid, None otherwise
        """
        try:
            result = self.wechat.parse_payment_result(xml_data)
            return result

        except WeChatPayException as e:
            logger.error(f"[WeChat Pay] Error verifying callback: {e}")
            return None
        except Exception as e:
            logger.error(f"[WeChat Pay] Unexpected error parsing callback: {e}")
            return None

    def query_alipay_order(self, order_no: str) -> Optional[Dict]:
        """
        Query Alipay order status

        Args:
            order_no: Order number

        Returns:
            Order status data or None
        """
        try:
            result = self.alipay.api_alipay_trade_query(out_trade_no=order_no)
            return result

        except Exception as e:
            logger.error(f"[Alipay] Error querying order {order_no}: {e}")
            return None

    def query_wechat_order(self, order_no: str) -> Optional[Dict]:
        """
        Query WeChat Pay order status

        Args:
            order_no: Order number

        Returns:
            Order status data or None
        """
        try:
            result = self.wechat.order.query(out_trade_no=order_no)
            return result

        except WeChatPayException as e:
            logger.error(f"[WeChat Pay] Error querying order {order_no}: {e}")
            return None
        except Exception as e:
            logger.error(f"[WeChat Pay] Unexpected error querying order {order_no}: {e}")
            return None

    async def verify_apple_receipt(self, receipt_data: str) -> Dict:
        """
        Verify Apple IAP receipt with Apple servers

        Args:
            receipt_data: Base64 encoded receipt data from iOS

        Returns:
            Dictionary with verification result:
            {
                'success': bool,
                'message': str,
                'purchase_info': {
                    'product_id': str,
                    'transaction_id': str,
                    'purchase_date': datetime,
                    'expires_date': datetime (optional, for subscriptions)
                }
            }
        """
        try:
            # Prepare request payload
            payload = {
                'receipt-data': receipt_data,
                'password': settings.APPLE_SHARED_SECRET,
                'exclude-old-transactions': True
            }

            # Try production environment first
            verify_url = settings.APPLE_VERIFY_URL_PRODUCTION if not settings.APPLE_SANDBOX_MODE else settings.APPLE_VERIFY_URL_SANDBOX

            logger.info(f"[Apple IAP] Verifying receipt with Apple ({'sandbox' if settings.APPLE_SANDBOX_MODE else 'production'})")

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(verify_url, json=payload)
                result = response.json()

            status = result.get('status')

            # Status 21007 means receipt is from sandbox but sent to production
            # Retry with sandbox URL
            if status == 21007 and not settings.APPLE_SANDBOX_MODE:
                logger.info("[Apple IAP] Receipt is from sandbox, retrying with sandbox URL")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(settings.APPLE_VERIFY_URL_SANDBOX, json=payload)
                    result = response.json()
                status = result.get('status')

            # Status 0 means success
            if status != 0:
                error_messages = {
                    21000: "The App Store could not read the JSON object you provided",
                    21002: "The data in the receipt-data property was malformed",
                    21003: "The receipt could not be authenticated",
                    21004: "The shared secret you provided does not match",
                    21005: "The receipt server is not currently available",
                    21006: "This receipt is valid but the subscription has expired",
                    21007: "This receipt is from the test environment",
                    21008: "This receipt is from the production environment",
                    21009: "Internal data access error",
                    21010: "The user account cannot be found or has been deleted"
                }

                error_msg = error_messages.get(status, f"Unknown error (status: {status})")
                logger.error(f"[Apple IAP] Receipt verification failed: {error_msg}")

                return {
                    'success': False,
                    'message': error_msg,
                    'status_code': status
                }

            # Extract receipt info
            receipt = result.get('receipt', {})
            in_app = receipt.get('in_app', [])

            # Also check latest_receipt_info for subscriptions
            latest_receipt_info = result.get('latest_receipt_info', [])

            # Get most recent purchase
            purchase = None
            if latest_receipt_info:
                # For subscriptions, use latest_receipt_info
                purchase = latest_receipt_info[0]
            elif in_app:
                # For non-consumable/consumable, use in_app
                purchase = in_app[0]
            else:
                logger.error("[Apple IAP] No purchase found in receipt")
                return {
                    'success': False,
                    'message': 'No purchase found in receipt'
                }

            # Extract purchase information
            product_id = purchase.get('product_id')
            transaction_id = purchase.get('transaction_id')
            purchase_date_ms = purchase.get('purchase_date_ms')
            expires_date_ms = purchase.get('expires_date_ms')

            # Convert timestamps
            purchase_date = datetime.fromtimestamp(int(purchase_date_ms) / 1000) if purchase_date_ms else None
            expires_date = datetime.fromtimestamp(int(expires_date_ms) / 1000) if expires_date_ms else None

            logger.info(f"[Apple IAP] Receipt verified successfully: product={product_id}, transaction={transaction_id}")

            return {
                'success': True,
                'message': 'Receipt verified successfully',
                'purchase_info': {
                    'product_id': product_id,
                    'transaction_id': transaction_id,
                    'purchase_date': purchase_date,
                    'expires_date': expires_date,
                    'raw_receipt': result
                }
            }

        except httpx.TimeoutException as e:
            logger.error(f"[Apple IAP] Timeout verifying receipt: {e}")
            return {
                'success': False,
                'message': 'Timeout connecting to Apple servers'
            }
        except httpx.HTTPError as e:
            logger.error(f"[Apple IAP] HTTP error verifying receipt: {e}")
            return {
                'success': False,
                'message': f'HTTP error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"[Apple IAP] Unexpected error verifying receipt: {e}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }

    @property
    def google_play(self):
        """
        Get or create Google Play Developer API client instance

        Returns:
            Google Play Developer API service object
        """
        if self._google_play_client is None:
            if not settings.GOOGLE_PLAY_SERVICE_ACCOUNT_FILE:
                logger.warning("[Google Play] Service account file not configured")
                return None

            if not os.path.exists(settings.GOOGLE_PLAY_SERVICE_ACCOUNT_FILE):
                logger.warning(f"[Google Play] Service account file not found: {settings.GOOGLE_PLAY_SERVICE_ACCOUNT_FILE}")
                return None

            try:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_PLAY_SERVICE_ACCOUNT_FILE,
                    scopes=['https://www.googleapis.com/auth/androidpublisher']
                )
                self._google_play_client = build('androidpublisher', 'v3', credentials=credentials)
                logger.info("[Google Play] API client initialized successfully")
            except Exception as e:
                logger.error(f"[Google Play] Failed to initialize API client: {e}")
                return None

        return self._google_play_client

    async def verify_google_play_purchase(
        self,
        purchase_token: str,
        product_id: str
    ) -> Dict:
        """
        Verify Google Play subscription purchase

        Args:
            purchase_token: Purchase token from Google Play
            product_id: Product ID (subscription ID)

        Returns:
            Dictionary with verification result:
            {
                'success': bool,
                'message': str,
                'purchase_info': {
                    'product_id': str,
                    'order_id': str,
                    'purchase_time': datetime,
                    'expiry_time': datetime
                }
            }
        """
        try:
            if not self.google_play:
                return {
                    'success': False,
                    'message': 'Google Play API client not available'
                }

            logger.info(f"[Google Play] Verifying purchase: product={product_id}")

            # Call Google Play Developer API
            result = self.google_play.purchases().subscriptions().get(
                packageName=settings.GOOGLE_PLAY_PACKAGE_NAME,
                subscriptionId=product_id,
                token=purchase_token
            ).execute()

            # Check payment state
            # 0 = Payment pending
            # 1 = Payment received
            # 2 = Free trial
            # 3 = Pending deferred upgrade/downgrade
            payment_state = result.get('paymentState')

            if payment_state != 1:
                payment_state_names = {
                    0: 'Payment pending',
                    2: 'Free trial',
                    3: 'Pending deferred upgrade/downgrade'
                }
                state_name = payment_state_names.get(payment_state, f'Unknown state: {payment_state}')
                logger.warning(f"[Google Play] Invalid payment state: {state_name}")
                return {
                    'success': False,
                    'message': f'Payment not completed: {state_name}'
                }

            # Extract purchase information
            order_id = result.get('orderId')
            start_time_millis = result.get('startTimeMillis')
            expiry_time_millis = result.get('expiryTimeMillis')

            # Convert timestamps
            purchase_time = datetime.fromtimestamp(int(start_time_millis) / 1000) if start_time_millis else None
            expiry_time = datetime.fromtimestamp(int(expiry_time_millis) / 1000) if expiry_time_millis else None

            logger.info(f"[Google Play] Purchase verified successfully: order={order_id}")

            return {
                'success': True,
                'message': 'Purchase verified successfully',
                'purchase_info': {
                    'product_id': product_id,
                    'order_id': order_id,
                    'purchase_token': purchase_token,
                    'purchase_time': purchase_time,
                    'expiry_time': expiry_time,
                    'auto_renewing': result.get('autoRenewing', False),
                    'raw_result': result
                }
            }

        except HttpError as e:
            error_content = e.content.decode('utf-8') if e.content else 'No error content'
            logger.error(f"[Google Play] HTTP error verifying purchase: {e.resp.status} - {error_content}")
            return {
                'success': False,
                'message': f'Google Play API error: {e.resp.status}'
            }
        except Exception as e:
            logger.error(f"[Google Play] Unexpected error verifying purchase: {e}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }
