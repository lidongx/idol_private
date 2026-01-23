"""
Payment API router
Story 7.2: 支付宝与微信支付集成
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User
from app.services.payment_service import PaymentService
from app.services.subscription_service import SubscriptionService
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


# Request models
class InitiatePaymentRequest(BaseModel):
    """Request model for initiating payment"""
    order_no: str
    payment_method: str  # 'alipay' or 'wechat'


class VerifyAppleReceiptRequest(BaseModel):
    """Request model for verifying Apple receipt"""
    receipt_data: str  # Base64 encoded receipt data from iOS
    order_no: Optional[str] = None  # Optional order number to link


# Response models
class PaymentResponse(BaseModel):
    """Response model for payment initiation"""
    success: bool
    order_no: str
    payment_method: str
    payment_url: Optional[str] = None  # For Alipay
    code_url: Optional[str] = None     # For WeChat QR code
    amount: float
    message: str


class PaymentStatusResponse(BaseModel):
    """Response model for payment status query"""
    order_no: str
    status: str
    paid: bool
    amount: float
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None


class AppleReceiptVerificationResponse(BaseModel):
    """Response model for Apple receipt verification"""
    success: bool
    message: str
    subscription_activated: bool = False
    order_no: Optional[str] = None
    expires_at: Optional[str] = None


class VerifyGooglePlayPurchaseRequest(BaseModel):
    """Request model for verifying Google Play purchase"""
    purchase_token: str  # Purchase token from Google Play
    product_id: str      # Product/subscription ID
    order_no: Optional[str] = None  # Optional order number to link


class GooglePlayVerificationResponse(BaseModel):
    """Response model for Google Play purchase verification"""
    success: bool
    message: str
    subscription_activated: bool = False
    order_no: Optional[str] = None
    expires_at: Optional[str] = None


@router.post(
    "/initiate",
    response_model=PaymentResponse,
    summary="发起支付",
    description="为订单发起支付宝或微信支付"
)
def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate payment for an order

    Supports:
    - Alipay: Returns payment_url for redirect
    - WeChat Pay: Returns code_url for QR code display

    Body:
    - order_no: Order number to pay for
    - payment_method: Payment method (alipay or wechat)

    Returns:
    - Payment details including payment_url or code_url
    """
    try:
        subscription_service = SubscriptionService(db)
        payment_service = PaymentService()

        # Get order and verify ownership
        order = subscription_service.get_order_by_no(request.order_no)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {request.order_no} not found"
            )

        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this order"
            )

        if order.status != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order {request.order_no} cannot be paid (status: {order.status})"
            )

        # Create payment based on method
        if request.payment_method == 'alipay':
            payment_data = payment_service.create_alipay_payment(order)
            return PaymentResponse(
                success=True,
                order_no=order.order_no,
                payment_method='alipay',
                payment_url=payment_data['payment_url'],
                amount=payment_data['amount'],
                message="请跳转到支付宝完成支付"
            )

        elif request.payment_method == 'wechat':
            payment_data = payment_service.create_wechat_payment(order)
            return PaymentResponse(
                success=True,
                order_no=order.order_no,
                payment_method='wechat',
                code_url=payment_data['code_url'],
                amount=payment_data['amount'],
                message="请扫描二维码完成支付"
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported payment method: {request.payment_method}"
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发起支付失败"
        )


@router.post(
    "/alipay/notify",
    summary="支付宝支付回调",
    description="接收支付宝支付结果通知"
)
async def alipay_notify(request: Request, db: Session = Depends(get_db)):
    """
    Alipay payment callback handler

    This endpoint is called by Alipay when payment status changes.
    It verifies the signature and updates the order status.

    Returns:
    - "success" if processed successfully
    - "fail" if verification or processing fails
    """
    try:
        # Get form data from Alipay callback
        form_data = await request.form()
        data = dict(form_data)

        logger.info(f"[Alipay Notify] Received callback for order: {data.get('out_trade_no')}")

        # Verify signature
        payment_service = PaymentService()
        signature = data.get('sign', '')

        if not payment_service.verify_alipay_callback(data, signature):
            logger.error("[Alipay Notify] Signature verification failed")
            return Response(content="fail", media_type="text/plain")

        # Extract payment information
        order_no = data.get('out_trade_no')
        trade_status = data.get('trade_status')
        trade_no = data.get('trade_no')  # Alipay transaction ID

        if not order_no:
            logger.error("[Alipay Notify] Missing order_no")
            return Response(content="fail", media_type="text/plain")

        # Process payment based on status
        subscription_service = SubscriptionService(db)

        if trade_status in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
            # Payment successful
            try:
                order = subscription_service.process_payment_success(
                    order_no=order_no,
                    transaction_id=trade_no
                )
                logger.info(f"[Alipay Notify] Order {order_no} paid successfully")

            except ValueError as e:
                logger.warning(f"[Alipay Notify] Error processing payment: {e}")
                # Still return success to Alipay to avoid retries
                return Response(content="success", media_type="text/plain")

        elif trade_status == 'TRADE_CLOSED':
            # Payment failed or closed
            subscription_service.process_payment_failure(
                order_no=order_no,
                reason=trade_status
            )
            logger.info(f"[Alipay Notify] Order {order_no} closed")

        return Response(content="success", media_type="text/plain")

    except Exception as e:
        logger.error(f"[Alipay Notify] Error processing callback: {e}")
        return Response(content="fail", media_type="text/plain")


@router.post(
    "/wechat/notify",
    summary="微信支付回调",
    description="接收微信支付结果通知"
)
async def wechat_notify(request: Request, db: Session = Depends(get_db)):
    """
    WeChat Pay payment callback handler

    This endpoint is called by WeChat Pay when payment status changes.
    It verifies the signature and updates the order status.

    Returns:
    - XML response with return_code=SUCCESS if processed successfully
    - XML response with return_code=FAIL if verification or processing fails
    """
    try:
        # Get XML data from WeChat callback
        xml_data = await request.body()

        logger.info("[WeChat Notify] Received callback")

        # Verify and parse callback
        payment_service = PaymentService()
        result = payment_service.verify_wechat_callback(xml_data.decode('utf-8'))

        if not result:
            logger.error("[WeChat Notify] Signature verification failed")
            return Response(
                content='<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名验证失败]]></return_msg></xml>',
                media_type="application/xml"
            )

        # Extract payment information
        order_no = result.get('out_trade_no')
        transaction_id = result.get('transaction_id')
        result_code = result.get('result_code')

        if not order_no:
            logger.error("[WeChat Notify] Missing order_no")
            return Response(
                content='<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[缺少订单号]]></return_msg></xml>',
                media_type="application/xml"
            )

        # Process payment based on result
        subscription_service = SubscriptionService(db)

        if result_code == 'SUCCESS':
            # Payment successful
            try:
                order = subscription_service.process_payment_success(
                    order_no=order_no,
                    transaction_id=transaction_id
                )
                logger.info(f"[WeChat Notify] Order {order_no} paid successfully")

            except ValueError as e:
                logger.warning(f"[WeChat Notify] Error processing payment: {e}")
                # Still return success to WeChat to avoid retries

        else:
            # Payment failed
            subscription_service.process_payment_failure(
                order_no=order_no,
                reason=result_code
            )
            logger.info(f"[WeChat Notify] Order {order_no} payment failed")

        return Response(
            content='<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>',
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(f"[WeChat Notify] Error processing callback: {e}")
        return Response(
            content='<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[系统错误]]></return_msg></xml>',
            media_type="application/xml"
        )


@router.get(
    "/orders/{order_no}/status",
    response_model=PaymentStatusResponse,
    summary="查询订单支付状态",
    description="查询指定订单的支付状态"
)
def query_payment_status(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Query payment status for an order

    This endpoint can be used by frontend to poll order status
    after initiating payment.

    Returns:
    - Order payment status details
    """
    try:
        subscription_service = SubscriptionService(db)

        # Get order and verify ownership
        order = subscription_service.get_order_by_no(order_no)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_no} not found"
            )

        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this order"
            )

        return PaymentStatusResponse(
            order_no=order.order_no,
            status=order.status,
            paid=order.is_paid,
            amount=float(order.amount),
            payment_method=order.payment_method,
            transaction_id=order.transaction_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询支付状态失败"
        )


@router.post(
    "/apple/verify",
    response_model=AppleReceiptVerificationResponse,
    summary="验证Apple收据",
    description="验证Apple IAP收据并激活订阅"
)
async def verify_apple_receipt(
    request: VerifyAppleReceiptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Apple In-App Purchase receipt

    This endpoint is called by iOS client after successful purchase
    to verify the receipt with Apple servers and activate subscription.

    Body:
    - receipt_data: Base64 encoded receipt data from StoreKit
    - order_no: Optional order number to link (if created via /orders endpoint)

    Returns:
    - Verification result and subscription activation status
    """
    try:
        payment_service = PaymentService()
        subscription_service = SubscriptionService(db)

        # Verify receipt with Apple
        verification_result = await payment_service.verify_apple_receipt(
            receipt_data=request.receipt_data
        )

        if not verification_result['success']:
            return AppleReceiptVerificationResponse(
                success=False,
                message=verification_result.get('message', 'Receipt verification failed'),
                subscription_activated=False
            )

        # Extract purchase information
        purchase_info = verification_result['purchase_info']
        product_id = purchase_info['product_id']
        transaction_id = purchase_info['transaction_id']
        expires_date = purchase_info.get('expires_date')

        # Determine plan type from product ID
        plan_type = None
        if 'monthly' in product_id:
            plan_type = 'monthly'
        elif 'yearly' in product_id:
            plan_type = 'yearly'
        else:
            raise ValueError(f"Unknown product ID: {product_id}")

        # Get or create order
        order_no = request.order_no
        if order_no:
            # Link to existing order
            order = subscription_service.get_order_by_no(order_no)
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order {order_no} not found"
                )
            if order.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Order does not belong to current user"
                )

            # Process payment success
            order = subscription_service.process_payment_success(
                order_no=order_no,
                transaction_id=transaction_id
            )
        else:
            # Create new order for this IAP
            # Get plan by type
            plans = subscription_service.get_all_plans()
            plan = next((p for p in plans if p.plan_type == plan_type), None)

            if not plan:
                raise ValueError(f"Plan not found for type: {plan_type}")

            # Create order
            order = subscription_service.create_order(
                user_id=current_user.id,
                plan_id=plan.id,
                payment_method='apple_iap'
            )

            # Process payment success immediately
            order = subscription_service.process_payment_success(
                order_no=order.order_no,
                transaction_id=transaction_id
            )

        logger.info(f"[Apple IAP] Subscription activated for user {current_user.id}, order {order.order_no}")

        return AppleReceiptVerificationResponse(
            success=True,
            message="订阅已成功激活",
            subscription_activated=True,
            order_no=order.order_no,
            expires_at=order.expires_at.isoformat() if order.expires_at else None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Apple IAP] Error verifying receipt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证收据失败"
        )


@router.post(
    "/apple/notify",
    summary="Apple Server-to-Server通知",
    description="接收Apple IAP服务器通知（续费、退款等）"
)
async def apple_server_notification(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Apple Server-to-Server Notification handler

    This endpoint receives notifications from Apple about subscription events:
    - INITIAL_BUY: First time purchase
    - DID_RENEW: Subscription renewed
    - DID_FAIL_TO_RENEW: Renewal failed
    - DID_CHANGE_RENEWAL_STATUS: User changed auto-renew settings
    - CANCEL: Subscription was canceled (refund)
    - REFUND: Purchase was refunded

    Apple will send these notifications automatically.
    Documentation: https://developer.apple.com/documentation/appstoreservernotifications

    Returns:
    - 200 OK to acknowledge receipt
    """
    try:
        # Get JSON data from Apple
        data = await request.json()

        logger.info(f"[Apple Notification] Received: {data.get('notification_type')}")

        notification_type = data.get('notification_type')

        # Extract unified receipt info
        unified_receipt = data.get('unified_receipt', {})
        latest_receipt_info = unified_receipt.get('latest_receipt_info', [])

        if not latest_receipt_info:
            logger.warning("[Apple Notification] No receipt info found")
            return Response(content="OK", media_type="text/plain")

        # Get most recent receipt
        receipt = latest_receipt_info[0]
        transaction_id = receipt.get('transaction_id')
        product_id = receipt.get('product_id')
        expires_date_ms = receipt.get('expires_date_ms')

        payment_service = PaymentService()
        subscription_service = SubscriptionService(db)

        # Find order by transaction ID
        order = subscription_service.get_order_by_transaction_id(transaction_id)

        if not order:
            logger.warning(f"[Apple Notification] Order not found for transaction {transaction_id}")
            return Response(content="OK", media_type="text/plain")

        # Handle different notification types
        if notification_type == 'INITIAL_BUY':
            logger.info(f"[Apple Notification] Initial purchase: {order.order_no}")
            # Already handled by verify endpoint

        elif notification_type == 'DID_RENEW':
            logger.info(f"[Apple Notification] Subscription renewed: {order.order_no}")
            # Update expiry date
            subscription_service.renew_subscription(
                user_id=order.user_id,
                expires_date_ms=int(expires_date_ms)
            )

        elif notification_type == 'DID_FAIL_TO_RENEW':
            logger.warning(f"[Apple Notification] Renewal failed: {order.order_no}")
            # Optionally send notification to user

        elif notification_type == 'DID_CHANGE_RENEWAL_STATUS':
            auto_renew_status = data.get('auto_renew_status')
            logger.info(f"[Apple Notification] Auto-renew changed to {auto_renew_status}: {order.order_no}")

        elif notification_type in ['CANCEL', 'REFUND']:
            logger.info(f"[Apple Notification] Subscription canceled/refunded: {order.order_no}")
            # Mark order as refunded and downgrade user
            subscription_service.process_refund(order.order_no)

        return Response(content="OK", media_type="text/plain")

    except Exception as e:
        logger.error(f"[Apple Notification] Error processing notification: {e}")
        # Return 200 OK even on error to prevent Apple from retrying
        return Response(content="OK", media_type="text/plain")


@router.post(
    "/google/verify",
    response_model=GooglePlayVerificationResponse,
    summary="验证Google Play购买",
    description="验证Google Play购买并激活订阅"
)
async def verify_google_play_purchase(
    request: VerifyGooglePlayPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Google Play subscription purchase

    This endpoint is called by Android client after successful purchase
    to verify the purchase with Google Play Developer API and activate subscription.

    Body:
    - purchase_token: Purchase token from Google Play
    - product_id: Product/subscription ID
    - order_no: Optional order number to link (if created via /orders endpoint)

    Returns:
    - Verification result and subscription activation status
    """
    try:
        payment_service = PaymentService()
        subscription_service = SubscriptionService(db)

        # Verify purchase with Google Play
        verification_result = await payment_service.verify_google_play_purchase(
            purchase_token=request.purchase_token,
            product_id=request.product_id
        )

        if not verification_result['success']:
            return GooglePlayVerificationResponse(
                success=False,
                message=verification_result.get('message', 'Purchase verification failed'),
                subscription_activated=False
            )

        # Extract purchase information
        purchase_info = verification_result['purchase_info']
        order_id = purchase_info['order_id']  # Google Play order ID
        product_id = purchase_info['product_id']

        # Determine plan type from product ID
        plan_type = None
        if 'monthly' in product_id:
            plan_type = 'monthly'
        elif 'yearly' in product_id:
            plan_type = 'yearly'
        else:
            raise ValueError(f"Unknown product ID: {product_id}")

        # Get or create order
        order_no = request.order_no
        if order_no:
            # Link to existing order
            order = subscription_service.get_order_by_no(order_no)
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order {order_no} not found"
                )
            if order.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Order does not belong to current user"
                )

            # Process payment success
            order = subscription_service.process_payment_success(
                order_no=order_no,
                transaction_id=order_id
            )
        else:
            # Create new order for this purchase
            # Get plan by type
            plans = subscription_service.get_all_plans()
            plan = next((p for p in plans if p.plan_type == plan_type), None)

            if not plan:
                raise ValueError(f"Plan not found for type: {plan_type}")

            # Create order
            order = subscription_service.create_order(
                user_id=current_user.id,
                plan_id=plan.id,
                payment_method='google_play'
            )

            # Process payment success immediately
            order = subscription_service.process_payment_success(
                order_no=order.order_no,
                transaction_id=order_id
            )

        logger.info(f"[Google Play] Subscription activated for user {current_user.id}, order {order.order_no}")

        return GooglePlayVerificationResponse(
            success=True,
            message="订阅已成功激活",
            subscription_activated=True,
            order_no=order.order_no,
            expires_at=order.expires_at.isoformat() if order.expires_at else None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Google Play] Error verifying purchase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证购买失败"
        )


@router.post(
    "/google/notify",
    summary="Google Play实时开发者通知",
    description="接收Google Play实时开发者通知（续费、取消等）"
)
async def google_play_notification(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Google Play Real-time Developer Notification handler

    This endpoint receives notifications from Google Play about subscription events:
    - SUBSCRIPTION_PURCHASED: Initial purchase
    - SUBSCRIPTION_RENEWED: Subscription renewed
    - SUBSCRIPTION_CANCELED: User canceled subscription
    - SUBSCRIPTION_IN_GRACE_PERIOD: Payment failed, in grace period
    - SUBSCRIPTION_REVOKED: Subscription revoked (refund)

    Google sends these notifications as Cloud Pub/Sub messages.
    Documentation: https://developer.android.com/google/play/billing/rtdn-reference

    Returns:
    - 200 OK to acknowledge receipt
    """
    try:
        # Get JSON data from Google Play (Pub/Sub message format)
        data = await request.json()

        logger.info(f"[Google Play Notification] Received: {data}")

        # Extract Pub/Sub message
        message = data.get('message', {})
        if not message:
            logger.warning("[Google Play Notification] No message in payload")
            return Response(content="OK", media_type="text/plain")

        # Decode base64 data
        import base64
        import json as json_lib

        message_data = message.get('data', '')
        if not message_data:
            logger.warning("[Google Play Notification] No data in message")
            return Response(content="OK", media_type="text/plain")

        decoded_data = base64.b64decode(message_data).decode('utf-8')
        notification_data = json_lib.loads(decoded_data)

        # Extract notification details
        notification_type = notification_data.get('notificationType')
        subscription_notification = notification_data.get('subscriptionNotification', {})

        purchase_token = subscription_notification.get('purchaseToken')
        subscription_id = subscription_notification.get('subscriptionId')

        if not purchase_token:
            logger.warning("[Google Play Notification] No purchase token found")
            return Response(content="OK", media_type="text/plain")

        payment_service = PaymentService()
        subscription_service = SubscriptionService(db)

        # Handle different notification types
        # Notification type codes:
        # 1 = SUBSCRIPTION_RECOVERED
        # 2 = SUBSCRIPTION_RENEWED
        # 3 = SUBSCRIPTION_CANCELED
        # 4 = SUBSCRIPTION_PURCHASED
        # 5 = SUBSCRIPTION_ON_HOLD
        # 6 = SUBSCRIPTION_IN_GRACE_PERIOD
        # 7 = SUBSCRIPTION_RESTARTED
        # 8 = SUBSCRIPTION_PRICE_CHANGE_CONFIRMED
        # 9 = SUBSCRIPTION_DEFERRED
        # 10 = SUBSCRIPTION_PAUSED
        # 11 = SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED
        # 12 = SUBSCRIPTION_REVOKED
        # 13 = SUBSCRIPTION_EXPIRED

        if notification_type == 4:  # SUBSCRIPTION_PURCHASED
            logger.info(f"[Google Play Notification] Initial purchase: {purchase_token}")
            # Already handled by verify endpoint

        elif notification_type == 2:  # SUBSCRIPTION_RENEWED
            logger.info(f"[Google Play Notification] Subscription renewed: {purchase_token}")
            # Verify purchase to get new expiry date
            verification = await payment_service.verify_google_play_purchase(
                purchase_token=purchase_token,
                product_id=subscription_id
            )
            if verification['success']:
                purchase_info = verification['purchase_info']
                expiry_time = purchase_info.get('expiry_time')
                if expiry_time:
                    # Update user subscription expiry
                    expiry_ms = int(expiry_time.timestamp() * 1000)
                    # Find user by purchase token (need to store this mapping)
                    # For now, log it
                    logger.info(f"[Google Play Notification] New expiry: {expiry_time}")

        elif notification_type == 3:  # SUBSCRIPTION_CANCELED
            logger.info(f"[Google Play Notification] Subscription canceled: {purchase_token}")
            # User canceled but subscription remains active until expiry

        elif notification_type == 12:  # SUBSCRIPTION_REVOKED (refund)
            logger.info(f"[Google Play Notification] Subscription revoked: {purchase_token}")
            # Find and process refund
            # (Need to store purchase_token mapping to order)

        elif notification_type == 13:  # SUBSCRIPTION_EXPIRED
            logger.info(f"[Google Play Notification] Subscription expired: {purchase_token}")
            # Subscription expired, will be handled by daily expiry check

        return Response(content="OK", media_type="text/plain")

    except Exception as e:
        logger.error(f"[Google Play Notification] Error processing notification: {e}")
        # Return 200 OK even on error to prevent Google from retrying
        return Response(content="OK", media_type="text/plain")
