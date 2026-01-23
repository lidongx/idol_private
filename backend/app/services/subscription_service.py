"""
SubscriptionService - Service for managing subscriptions and orders
Story 7.1: 订阅套餐数据模型与定价策略
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import secrets

from app.models.subscription_plan import SubscriptionPlan
from app.models.order import Order
from app.models.user import User
from app.models.subscription_log import SubscriptionLog
from app.models.refund_request import RefundRequest


class SubscriptionService:
    """Service for managing subscriptions and orders"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_plans(self, include_inactive: bool = False) -> List[SubscriptionPlan]:
        """
        Get all subscription plans

        Args:
            include_inactive: Whether to include inactive plans

        Returns:
            List of SubscriptionPlan objects
        """
        query = self.db.query(SubscriptionPlan)

        if not include_inactive:
            query = query.filter(SubscriptionPlan.is_active == True)

        return query.order_by(SubscriptionPlan.sort_order).all()

    def get_plan_by_id(self, plan_id: int) -> Optional[SubscriptionPlan]:
        """
        Get subscription plan by ID

        Args:
            plan_id: Plan ID

        Returns:
            SubscriptionPlan object or None
        """
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == plan_id
        ).first()

    def get_plan_by_type(self, plan_type: str) -> Optional[SubscriptionPlan]:
        """
        Get subscription plan by type

        Args:
            plan_type: Plan type (free, monthly, yearly)

        Returns:
            SubscriptionPlan object or None
        """
        return self.db.query(SubscriptionPlan).filter(
            and_(
                SubscriptionPlan.plan_type == plan_type,
                SubscriptionPlan.is_active == True
            )
        ).first()

    def generate_order_no(self) -> str:
        """
        Generate unique order number

        Format: IDL + YYYYMMDDHHMMSS + 4-digit random
        Example: IDL20260119123456ABCD

        Returns:
            Unique order number string
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = secrets.token_hex(2).upper()  # 4 hex characters
        order_no = f"IDL{timestamp}{random_suffix}"

        # Check if order_no already exists (very unlikely)
        existing = self.db.query(Order).filter(Order.order_no == order_no).first()
        if existing:
            # Add extra random characters if collision
            return self.generate_order_no()

        return order_no

    def create_order(
        self,
        user_id: int,
        plan_id: int,
        payment_method: str = None
    ) -> Order:
        """
        Create a new order

        Args:
            user_id: User ID
            plan_id: Subscription plan ID
            payment_method: Payment method (alipay, wechat, etc.)

        Returns:
            Created Order object

        Raises:
            ValueError: If plan not found or invalid
        """
        # Validate plan
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        if not plan.is_active:
            raise ValueError(f"Plan {plan_id} is not active")

        # Don't allow creating orders for free plan
        if plan.plan_type == SubscriptionPlan.TYPE_FREE:
            raise ValueError("Cannot create order for free plan")

        # Generate order number
        order_no = self.generate_order_no()

        # Create order
        order = Order(
            order_no=order_no,
            user_id=user_id,
            plan_id=plan_id,
            amount=plan.price_cny,
            payment_method=payment_method,
            status=Order.STATUS_PENDING
        )

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return order

    def get_order_by_no(self, order_no: str) -> Optional[Order]:
        """
        Get order by order number

        Args:
            order_no: Order number

        Returns:
            Order object or None
        """
        return self.db.query(Order).filter(
            Order.order_no == order_no
        ).first()

    def get_user_orders(
        self,
        user_id: int,
        status: str = None,
        limit: int = 50
    ) -> List[Order]:
        """
        Get orders for a user

        Args:
            user_id: User ID
            status: Filter by status (optional)
            limit: Maximum number of orders to return

        Returns:
            List of Order objects
        """
        query = self.db.query(Order).filter(Order.user_id == user_id)

        if status:
            query = query.filter(Order.status == status)

        return query.order_by(Order.created_at.desc()).limit(limit).all()

    def get_active_subscription(self, user_id: int) -> Optional[Order]:
        """
        Get user's active subscription

        Args:
            user_id: User ID

        Returns:
            Active Order object or None
        """
        # Find paid orders that haven't expired
        orders = self.db.query(Order).filter(
            and_(
                Order.user_id == user_id,
                Order.status == Order.STATUS_PAID,
                or_(
                    Order.expires_at.is_(None),
                    Order.expires_at > datetime.utcnow()
                )
            )
        ).order_by(Order.expires_at.desc()).all()

        return orders[0] if orders else None

    def check_user_has_feature(self, user_id: int, feature_key: str) -> bool:
        """
        Check if user has a specific feature access

        Args:
            user_id: User ID
            feature_key: Feature key (e.g., 'exclusive_content')

        Returns:
            True if user has the feature, False otherwise
        """
        active_sub = self.get_active_subscription(user_id)

        if not active_sub or not active_sub.plan:
            # User has no active subscription, check free plan
            free_plan = self.get_plan_by_type(SubscriptionPlan.TYPE_FREE)
            return free_plan.get_feature(feature_key, False) if free_plan else False

        return active_sub.plan.get_feature(feature_key, False)

    def get_user_message_limit(self, user_id: int) -> int:
        """
        Get user's daily message limit

        Args:
            user_id: User ID

        Returns:
            Daily message limit (-1 means unlimited)
        """
        active_sub = self.get_active_subscription(user_id)

        if not active_sub or not active_sub.plan:
            # User has no active subscription, return free plan limit
            free_plan = self.get_plan_by_type(SubscriptionPlan.TYPE_FREE)
            return free_plan.messages_per_day if free_plan else 20

        return active_sub.plan.messages_per_day

    def cancel_order(self, order_no: str) -> Dict:
        """
        Cancel a pending order

        Args:
            order_no: Order number

        Returns:
            Result dictionary

        Raises:
            ValueError: If order not found or cannot be cancelled
        """
        order = self.get_order_by_no(order_no)

        if not order:
            raise ValueError(f"Order {order_no} not found")

        if order.status != Order.STATUS_PENDING:
            raise ValueError(f"Order {order_no} cannot be cancelled (status: {order.status})")

        order.mark_as_cancelled()
        self.db.commit()

        return {
            'success': True,
            'order_no': order_no,
            'message': 'Order cancelled successfully'
        }

    def get_subscription_stats(self, user_id: int) -> Dict:
        """
        Get subscription statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with subscription statistics
        """
        active_sub = self.get_active_subscription(user_id)
        all_orders = self.get_user_orders(user_id)

        paid_orders = [o for o in all_orders if o.status == Order.STATUS_PAID]
        total_spent = sum(float(o.amount) for o in paid_orders)

        result = {
            'has_active_subscription': active_sub is not None,
            'total_orders': len(all_orders),
            'total_spent': total_spent,
            'pending_orders': len([o for o in all_orders if o.status == Order.STATUS_PENDING]),
        }

        if active_sub:
            result['active_subscription'] = {
                'plan_name': active_sub.plan.plan_name if active_sub.plan else None,
                'expires_at': active_sub.expires_at.isoformat() if active_sub.expires_at else None,
                'days_remaining': active_sub.days_until_expiry,
                'features': active_sub.plan.features if active_sub.plan else {}
            }

        return result

    def process_payment_success(
        self,
        order_no: str,
        transaction_id: str = None,
        payment_data: Dict = None
    ) -> Order:
        """
        Process successful payment for an order and activate subscription

        This method performs the complete subscription activation flow:
        1. Mark order as paid
        2. Update user subscription status
        3. Record subscription log
        4. (Optional) Send success notification

        Args:
            order_no: Order number
            transaction_id: Payment transaction ID from payment gateway
            payment_data: Additional payment data (optional)

        Returns:
            Updated Order object

        Raises:
            ValueError: If order not found or already processed
        """
        order = self.get_order_by_no(order_no)

        if not order:
            raise ValueError(f"Order {order_no} not found")

        if order.status == Order.STATUS_PAID:
            # Order already paid, return existing order
            return order

        if order.status != Order.STATUS_PENDING:
            raise ValueError(
                f"Order {order_no} cannot be processed (status: {order.status})"
            )

        # 1. Mark order as paid
        order.mark_as_paid(transaction_id=transaction_id)

        # 2. Update user subscription status
        user = self.db.query(User).filter(User.id == order.user_id).first()
        if user:
            # Determine action type (activate or renew)
            is_renew = user.subscription_tier == 'premium'
            action = SubscriptionLog.ACTION_RENEW if is_renew else SubscriptionLog.ACTION_ACTIVATE

            # Update user subscription
            user.subscription_tier = 'premium'
            user.subscription_expires_at = order.expires_at

            # 3. Record subscription log
            subscription_log = SubscriptionLog(
                user_id=user.id,
                action=action,
                plan_id=order.plan_id,
                order_id=order.id,
                expires_at=order.expires_at,
                notes=f"Payment via {order.payment_method}, transaction: {transaction_id}"
            )
            self.db.add(subscription_log)

        self.db.commit()
        self.db.refresh(order)

        return order

    def process_payment_failure(
        self,
        order_no: str,
        reason: str = None
    ) -> Order:
        """
        Process failed payment for an order

        Args:
            order_no: Order number
            reason: Failure reason (optional)

        Returns:
            Updated Order object

        Raises:
            ValueError: If order not found
        """
        order = self.get_order_by_no(order_no)

        if not order:
            raise ValueError(f"Order {order_no} not found")

        if order.status != Order.STATUS_PENDING:
            # Only pending orders can be marked as failed
            return order

        # Mark order as failed
        order.mark_as_failed()
        self.db.commit()
        self.db.refresh(order)

        return order

    def get_order_by_transaction_id(self, transaction_id: str) -> Optional[Order]:
        """
        Get order by payment transaction ID

        Args:
            transaction_id: Transaction ID from payment provider

        Returns:
            Order object or None
        """
        return self.db.query(Order).filter(
            Order.transaction_id == transaction_id
        ).first()

    def renew_subscription(
        self,
        user_id: int,
        expires_date_ms: int
    ) -> bool:
        """
        Renew user subscription (for auto-renewable subscriptions)

        Args:
            user_id: User ID
            expires_date_ms: New expiry date in milliseconds (Unix timestamp)

        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Convert milliseconds to datetime
            expires_at = datetime.fromtimestamp(expires_date_ms / 1000)

            # Update user subscription
            user.subscription_expires_at = expires_at
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            return False

    def process_refund(self, order_no: str) -> bool:
        """
        Process refund for an order (used for Apple IAP refunds)

        Args:
            order_no: Order number

        Returns:
            True if successful, False otherwise
        """
        try:
            order = self.get_order_by_no(order_no)
            if not order:
                return False

            # Mark order as refunded
            order.status = Order.STATUS_REFUNDED
            self.db.commit()

            # Downgrade user to free tier
            user = self.db.query(User).filter(User.id == order.user_id).first()
            if user:
                user.subscription_tier = 'free'
                user.subscription_expires_at = None
                self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            return False

    def create_refund_request(
        self,
        user_id: int,
        order_id: int,
        reason: str,
        detailed_reason: str = None
    ) -> RefundRequest:
        """
        Create a refund request

        Args:
            user_id: User ID
            order_id: Order ID to refund
            reason: Refund reason code
            detailed_reason: Optional detailed explanation

        Returns:
            Created RefundRequest object

        Raises:
            ValueError: If order not found or not eligible for refund
        """
        # Validate order
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.user_id != user_id:
            raise ValueError("Order does not belong to user")

        if order.status != Order.STATUS_PAID:
            raise ValueError(f"Order cannot be refunded (status: {order.status})")

        # Check if refund request already exists
        existing = self.db.query(RefundRequest).filter(
            and_(
                RefundRequest.order_id == order_id,
                RefundRequest.status == RefundRequest.STATUS_PENDING
            )
        ).first()

        if existing:
            raise ValueError("Refund request already exists for this order")

        # Create refund request
        refund_request = RefundRequest(
            user_id=user_id,
            order_id=order_id,
            reason=reason,
            detailed_reason=detailed_reason,
            status=RefundRequest.STATUS_PENDING
        )

        self.db.add(refund_request)
        self.db.commit()
        self.db.refresh(refund_request)

        return refund_request

    def get_refund_requests(
        self,
        user_id: int = None,
        status: str = None,
        limit: int = 50
    ) -> List[RefundRequest]:
        """
        Get refund requests

        Args:
            user_id: Filter by user ID (optional)
            status: Filter by status (optional)
            limit: Maximum number of requests to return

        Returns:
            List of RefundRequest objects
        """
        query = self.db.query(RefundRequest)

        if user_id:
            query = query.filter(RefundRequest.user_id == user_id)

        if status:
            query = query.filter(RefundRequest.status == status)

        return query.order_by(RefundRequest.created_at.desc()).limit(limit).all()

    def process_refund_request(
        self,
        refund_id: int,
        approved: bool,
        admin_notes: str = None
    ) -> Dict:
        """
        Process a refund request (admin operation)

        Args:
            refund_id: Refund request ID
            approved: Whether to approve or reject
            admin_notes: Admin notes (optional)

        Returns:
            Result dictionary with status and message

        Raises:
            ValueError: If refund request not found or already processed
        """
        refund = self.db.query(RefundRequest).filter(
            RefundRequest.id == refund_id
        ).first()

        if not refund:
            raise ValueError(f"Refund request {refund_id} not found")

        if refund.status != RefundRequest.STATUS_PENDING:
            raise ValueError(f"Refund request already processed (status: {refund.status})")

        order = self.db.query(Order).filter(Order.id == refund.order_id).first()
        if not order:
            raise ValueError(f"Order {refund.order_id} not found")

        if approved:
            # TODO: Call payment provider refund API
            # For now, just mark as refunded in database

            # Mark order as refunded
            order.status = Order.STATUS_REFUNDED
            self.db.commit()

            # Downgrade user to free tier
            user = self.db.query(User).filter(User.id == order.user_id).first()
            if user:
                old_tier = user.subscription_tier
                user.subscription_tier = 'free'
                user.subscription_expires_at = None
                self.db.commit()

                # Record subscription log
                subscription_log = SubscriptionLog(
                    user_id=user.id,
                    action=SubscriptionLog.ACTION_REFUND,
                    plan_id=order.plan_id,
                    order_id=order.id,
                    expires_at=None,
                    notes=f"Refund approved - downgraded from {old_tier} to free"
                )
                self.db.add(subscription_log)

            # Update refund request
            refund.status = RefundRequest.STATUS_APPROVED
            refund.admin_notes = admin_notes
            refund.processed_at = datetime.utcnow()
            self.db.commit()

            return {
                'success': True,
                'message': 'Refund approved and processed',
                'refund_id': refund_id,
                'order_no': order.order_no
            }
        else:
            # Reject refund request
            refund.status = RefundRequest.STATUS_REJECTED
            refund.admin_notes = admin_notes
            refund.processed_at = datetime.utcnow()
            self.db.commit()

            return {
                'success': True,
                'message': 'Refund request rejected',
                'refund_id': refund_id
            }

    def cancel_subscription(self, user_id: int) -> Dict:
        """
        Cancel user's subscription (disable auto-renewal)

        Note: For Apple IAP and Google Play, users must cancel through
        the respective platform settings. This method is for web payments.

        Args:
            user_id: User ID

        Returns:
            Result dictionary

        Raises:
            ValueError: If user has no active subscription
        """
        active_sub = self.get_active_subscription(user_id)

        if not active_sub:
            raise ValueError("No active subscription found")

        # For platform subscriptions (Apple/Google), just inform user
        if active_sub.payment_method in ['apple_iap', 'google_play']:
            platform = 'App Store' if active_sub.payment_method == 'apple_iap' else 'Google Play'
            return {
                'success': False,
                'message': f'请前往{platform}管理订阅',
                'platform': active_sub.payment_method,
                'requires_platform_action': True
            }

        # For web payments, mark subscription for cancellation
        # TODO: Call payment provider API to cancel auto-renewal

        # Record subscription log
        subscription_log = SubscriptionLog(
            user_id=user_id,
            action=SubscriptionLog.ACTION_CANCEL,
            plan_id=active_sub.plan_id,
            order_id=active_sub.id,
            expires_at=active_sub.expires_at,
            notes=f"Subscription cancelled by user - will expire on {active_sub.expires_at}"
        )
        self.db.add(subscription_log)
        self.db.commit()

        return {
            'success': True,
            'message': '订阅已取消，将在到期后停止续费',
            'expires_at': active_sub.expires_at.isoformat() if active_sub.expires_at else None
        }
