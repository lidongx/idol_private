"""
Subscription API router
Story 7.1: 订阅套餐数据模型与定价策略
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.subscription_service import SubscriptionService
from app.routers.auth import get_current_user


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# Response models
class SubscriptionPlanResponse(BaseModel):
    """Response model for subscription plan"""
    id: int
    plan_name: str
    plan_type: str
    plan_type_display: str
    price_cny: float
    price_display: str
    duration_days: int
    duration_display: str
    features: dict
    is_active: bool
    sort_order: int
    created_at: str = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Response model for order"""
    id: int
    order_no: str
    user_id: int
    plan_id: int
    amount: float
    payment_method: Optional[str] = None
    payment_method_display: str
    status: str
    status_display: str
    paid_at: Optional[str] = None
    expires_at: Optional[str] = None
    transaction_id: Optional[str] = None
    is_active: bool
    days_until_expiry: int
    created_at: str
    plan: Optional[dict] = None

    class Config:
        from_attributes = True


class CreateOrderRequest(BaseModel):
    """Request model for creating order"""
    plan_id: int
    payment_method: str  # 'alipay', 'wechat', 'apple_iap', 'google_play'


class CreateOrderResponse(BaseModel):
    """Response model for created order"""
    success: bool
    order: OrderResponse
    message: str


class SubscriptionStatsResponse(BaseModel):
    """Response model for subscription statistics"""
    has_active_subscription: bool
    total_orders: int
    total_spent: float
    pending_orders: int
    active_subscription: Optional[dict] = None


class CancelOrderResponse(BaseModel):
    """Response model for cancel order"""
    success: bool
    order_no: str
    message: str


class RefundRequestRequest(BaseModel):
    """Request model for creating refund request"""
    order_id: int
    reason: str
    detailed_reason: Optional[str] = None


class RefundRequestResponse(BaseModel):
    """Response model for refund request"""
    id: int
    order_id: int
    reason: str
    reason_display: str
    detailed_reason: Optional[str]
    status: str
    status_display: str
    created_at: str

    class Config:
        from_attributes = True


class CancelSubscriptionResponse(BaseModel):
    """Response model for cancel subscription"""
    success: bool
    message: str
    expires_at: Optional[str] = None
    requires_platform_action: bool = False
    platform: Optional[str] = None


@router.get(
    "/plans",
    response_model=List[SubscriptionPlanResponse],
    summary="获取订阅套餐列表",
    description="获取所有可用的订阅套餐"
)
def get_subscription_plans(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all subscription plans

    Returns list of available subscription plans with:
    - Plan details (name, type, price, duration)
    - Feature list
    - Display information

    Query params:
    - include_inactive: Whether to include inactive plans (default: false)
    """
    subscription_service = SubscriptionService(db)
    plans = subscription_service.get_all_plans(include_inactive=include_inactive)

    return [SubscriptionPlanResponse(**plan.to_dict()) for plan in plans]


@router.get(
    "/plans/{plan_id}",
    response_model=SubscriptionPlanResponse,
    summary="获取订阅套餐详情",
    description="获取指定订阅套餐的详细信息"
)
def get_subscription_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    Get subscription plan details by ID

    Returns detailed information about a specific plan
    """
    subscription_service = SubscriptionService(db)
    plan = subscription_service.get_plan_by_id(plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found"
        )

    return SubscriptionPlanResponse(**plan.to_dict())


@router.post(
    "/orders",
    response_model=CreateOrderResponse,
    summary="创建订单",
    description="创建订阅购买订单"
)
def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a subscription purchase order

    Body:
    - plan_id: Subscription plan ID to purchase
    - payment_method: Payment method (alipay, wechat, apple_iap, google_play)

    Returns:
    - Created order details
    - Order status will be 'pending' initially
    - Frontend should proceed to payment flow
    """
    try:
        subscription_service = SubscriptionService(db)
        order = subscription_service.create_order(
            user_id=current_user.id,
            plan_id=request.plan_id,
            payment_method=request.payment_method
        )

        return CreateOrderResponse(
            success=True,
            order=OrderResponse(**order.to_dict(include_plan_details=True)),
            message="订单创建成功，请继续完成支付"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败"
        )


@router.get(
    "/orders",
    response_model=List[OrderResponse],
    summary="获取订单列表",
    description="获取当前用户的所有订单"
)
def get_user_orders(
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's orders

    Returns list of orders ordered by creation time (newest first)

    Query params:
    - status: Filter by status (pending, paid, failed, cancelled, refunded)
    - limit: Maximum number of orders to return (default: 50)
    """
    subscription_service = SubscriptionService(db)
    orders = subscription_service.get_user_orders(
        user_id=current_user.id,
        status=status_filter,
        limit=limit
    )

    return [OrderResponse(**order.to_dict(include_plan_details=True)) for order in orders]


@router.get(
    "/orders/{order_no}",
    response_model=OrderResponse,
    summary="获取订单详情",
    description="获取指定订单的详细信息"
)
def get_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details by order number

    Returns detailed information about a specific order
    """
    subscription_service = SubscriptionService(db)
    order = subscription_service.get_order_by_no(order_no)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_no} not found"
        )

    # Verify order belongs to current user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this order"
        )

    return OrderResponse(**order.to_dict(include_plan_details=True))


@router.get(
    "/active",
    response_model=Optional[OrderResponse],
    summary="获取当前激活的订阅",
    description="获取用户当前激活的订阅信息"
)
def get_active_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's active subscription

    Returns active subscription order if exists, null otherwise
    """
    subscription_service = SubscriptionService(db)
    active_sub = subscription_service.get_active_subscription(current_user.id)

    if not active_sub:
        return None

    return OrderResponse(**active_sub.to_dict(include_plan_details=True))


@router.get(
    "/stats",
    response_model=SubscriptionStatsResponse,
    summary="获取订阅统计",
    description="获取用户的订阅统计信息"
)
def get_subscription_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's subscription statistics

    Returns:
    - Whether user has active subscription
    - Total number of orders
    - Total amount spent
    - Pending orders count
    - Active subscription details (if any)
    """
    subscription_service = SubscriptionService(db)
    stats = subscription_service.get_subscription_stats(current_user.id)

    return SubscriptionStatsResponse(**stats)


@router.delete(
    "/orders/{order_no}",
    response_model=CancelOrderResponse,
    summary="取消订单",
    description="取消待支付的订单"
)
def cancel_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a pending order

    Only pending orders can be cancelled
    """
    subscription_service = SubscriptionService(db)

    # Verify order exists and belongs to user
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

    try:
        result = subscription_service.cancel_order(order_no)
        return CancelOrderResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error cancelling order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取消订单失败"
        )


@router.post(
    "/refund",
    response_model=RefundRequestResponse,
    summary="申请退款",
    description="为已支付订单申请退款"
)
def create_refund_request(
    request: RefundRequestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a refund request for a paid order

    Body:
    - order_id: Order ID to refund
    - reason: Refund reason code (not_satisfied, technical_issue, accidental_purchase, billing_error, other)
    - detailed_reason: Optional detailed explanation

    Returns:
    - Created refund request
    - Status will be 'pending' for admin review
    """
    try:
        subscription_service = SubscriptionService(db)
        refund_request = subscription_service.create_refund_request(
            user_id=current_user.id,
            order_id=request.order_id,
            reason=request.reason,
            detailed_reason=request.detailed_reason
        )

        return RefundRequestResponse(**refund_request.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error creating refund request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="申请退款失败"
        )


@router.get(
    "/refund/requests",
    response_model=List[RefundRequestResponse],
    summary="获取退款申请列表",
    description="获取用户的所有退款申请"
)
def get_refund_requests(
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's refund requests

    Returns list of refund requests ordered by creation time (newest first)

    Query params:
    - status: Filter by status (pending, approved, rejected)
    - limit: Maximum number of requests to return (default: 50)
    """
    subscription_service = SubscriptionService(db)
    refund_requests = subscription_service.get_refund_requests(
        user_id=current_user.id,
        status=status_filter,
        limit=limit
    )

    return [RefundRequestResponse(**req.to_dict()) for req in refund_requests]


@router.post(
    "/cancel",
    response_model=CancelSubscriptionResponse,
    summary="取消订阅",
    description="取消自动续费订阅"
)
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's auto-renewal subscription

    For Apple IAP and Google Play subscriptions, user must cancel through
    the respective platform settings. This endpoint will provide guidance.

    For web payments (Alipay/WeChat), this will cancel auto-renewal.

    Returns:
    - Success status
    - Message with cancellation details or platform guidance
    - Expiry date (subscription remains active until expiry)
    """
    try:
        subscription_service = SubscriptionService(db)
        result = subscription_service.cancel_subscription(current_user.id)

        return CancelSubscriptionResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取消订阅失败"
        )
