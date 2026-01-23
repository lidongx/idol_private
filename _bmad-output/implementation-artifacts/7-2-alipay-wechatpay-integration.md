# Story 7.2: 支付宝与微信支付集成

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-19

## Story

As a **用户**,
I want **通过支付宝或微信支付购买订阅**,
So that **快速便捷地完成支付**。

## Acceptance Criteria

### AC1: 支付SDK集成
- **Given** 需要支持支付宝和微信支付
- **When** 集成支付SDK
- **Then** 安装python-alipay-sdk和wechatpy依赖
- **And** 配置支付宝私钥、公钥、APPID
- **And** 配置微信支付商户ID、API密钥、证书

### AC2: 支付发起接口
- **Given** 用户已创建待支付订单
- **When** 调用支付发起接口
- **Then** 根据支付方式创建支付请求
- **And** 支付宝返回支付跳转URL
- **And** 微信支付返回二维码URL

### AC3: 支付回调处理
- **Given** 用户完成支付
- **When** 支付网关发送回调通知
- **Then** 验证回调签名
- **And** 更新订单状态为已支付
- **And** 设置订单过期时间
- **And** 返回成功响应给支付网关

---

## Implementation Details

### Dependencies Added

**backend/requirements.txt:**
```txt
# Payment SDKs
python-alipay-sdk==3.6.0
wechatpy==1.8.18
```

### Payment Configuration

**backend/app/config.py:**
```python
# Alipay Configuration
ALIPAY_APPID: str = ""
ALIPAY_PRIVATE_KEY: str = ""  # Path to private key file or key string
ALIPAY_PUBLIC_KEY: str = ""   # Path to Alipay public key file or key string
ALIPAY_SIGN_TYPE: str = "RSA2"
ALIPAY_DEBUG: bool = True  # True for sandbox, False for production
ALIPAY_RETURN_URL: str = "http://localhost:3000/payment/alipay/return"
ALIPAY_NOTIFY_URL: str = "http://localhost:8000/api/v1/payments/alipay/notify"

# WeChat Pay Configuration
WECHAT_APPID: str = ""
WECHAT_MCH_ID: str = ""       # Merchant ID
WECHAT_API_KEY: str = ""      # API v2 key
WECHAT_APICLIENT_CERT: str = ""  # Path to cert.pem
WECHAT_APICLIENT_KEY: str = ""   # Path to key.pem
WECHAT_NOTIFY_URL: str = "http://localhost:8000/api/v1/payments/wechat/notify"
```

---

## Files Created/Modified

### 新建文件 (2个)

#### Services
1. **backend/app/services/payment_service.py** (285 lines)
   - PaymentService for Alipay and WeChat Pay integration
   - Methods:
     * create_alipay_payment() - Create Alipay payment
     * create_wechat_payment() - Create WeChat Native (QR code) payment
     * verify_alipay_callback() - Verify Alipay callback signature
     * verify_wechat_callback() - Verify WeChat callback signature
     * query_alipay_order() - Query Alipay order status
     * query_wechat_order() - Query WeChat order status

#### Routers
2. **backend/app/routers/payment.py** (360 lines)
   - 4 API endpoints:
     * POST /api/v1/payments/initiate - 发起支付
     * POST /api/v1/payments/alipay/notify - 支付宝回调
     * POST /api/v1/payments/wechat/notify - 微信支付回调
     * GET /api/v1/payments/orders/{order_no}/status - 查询支付状态

### 修改文件 (4个)

3. **backend/requirements.txt**
   - 添加支付SDK依赖: python-alipay-sdk, wechatpy

4. **backend/app/config.py**
   - 添加支付配置参数(14个新配置项)

5. **backend/app/services/subscription_service.py**
   - 添加process_payment_success()方法
   - 添加process_payment_failure()方法

6. **backend/app/main.py**
   - 注册payment路由

---

## API Endpoints

### POST /api/v1/payments/initiate
发起支付

**Request Body:**
```json
{
  "order_no": "IDL20260119123456ABCD",
  "payment_method": "alipay"
}
```

**Response (支付宝):**
```json
{
  "success": true,
  "order_no": "IDL20260119123456ABCD",
  "payment_method": "alipay",
  "payment_url": "https://openapi.alipaydev.com/gateway.do?...",
  "amount": 28.0,
  "message": "请跳转到支付宝完成支付"
}
```

**Response (微信支付):**
```json
{
  "success": true,
  "order_no": "IDL20260119123456ABCD",
  "payment_method": "wechat",
  "code_url": "weixin://wxpay/bizpayurl?pr=xxxxx",
  "amount": 28.0,
  "message": "请扫描二维码完成支付"
}
```

### POST /api/v1/payments/alipay/notify
支付宝支付回调（由支付宝服务器调用）

**Request (Form Data from Alipay):**
- out_trade_no: 订单号
- trade_no: 支付宝交易号
- trade_status: TRADE_SUCCESS / TRADE_FINISHED / TRADE_CLOSED
- sign: 签名

**Response:**
```
success
```

### POST /api/v1/payments/wechat/notify
微信支付回调（由微信支付服务器调用）

**Request (XML from WeChat):**
```xml
<xml>
  <out_trade_no><![CDATA[IDL20260119123456ABCD]]></out_trade_no>
  <transaction_id><![CDATA[4200001234567890]]></transaction_id>
  <result_code><![CDATA[SUCCESS]]></result_code>
  ...
</xml>
```

**Response:**
```xml
<xml>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <return_msg><![CDATA[OK]]></return_msg>
</xml>
```

### GET /api/v1/payments/orders/{order_no}/status
查询订单支付状态

**Response:**
```json
{
  "order_no": "IDL20260119123456ABCD",
  "status": "paid",
  "paid": true,
  "amount": 28.0,
  "payment_method": "alipay",
  "transaction_id": "2026011922001234567890"
}
```

---

## Business Logic Highlights

### Alipay Payment Flow

```python
def create_alipay_payment(self, order: Order) -> Dict:
    # Create Alipay payment request
    order_string = self.alipay.api_alipay_trade_page_pay(
        out_trade_no=order.order_no,
        total_amount=str(float(order.amount)),
        subject=f"{order.plan.plan_name} - idol_private订阅",
        return_url=settings.ALIPAY_RETURN_URL,
        notify_url=settings.ALIPAY_NOTIFY_URL,
        product_code="FAST_INSTANT_TRADE_PAY"
    )

    # Construct payment URL (sandbox or production)
    if settings.ALIPAY_DEBUG:
        payment_url = f"https://openapi.alipaydev.com/gateway.do?{order_string}"
    else:
        payment_url = f"https://openapi.alipay.com/gateway.do?{order_string}"

    return {
        'payment_method': 'alipay',
        'order_no': order.order_no,
        'payment_url': payment_url,
        'amount': float(order.amount)
    }
```

### WeChat Pay Native Flow

```python
def create_wechat_payment(self, order: Order) -> Dict:
    # Create WeChat Pay Native order
    result = self.wechat.order.create(
        trade_type='NATIVE',
        out_trade_no=order.order_no,
        total_fee=int(float(order.amount) * 100),  # Convert to cents
        body=f"{order.plan.plan_name} - idol_private订阅",
        notify_url=settings.WECHAT_NOTIFY_URL
    )

    if result.get('return_code') != 'SUCCESS':
        raise ValueError(f"WeChat Pay error: {result.get('err_code_des')}")

    return {
        'payment_method': 'wechat',
        'order_no': order.order_no,
        'code_url': result.get('code_url'),  # QR code URL
        'amount': float(order.amount)
    }
```

### Payment Callback Verification

**Alipay:**
```python
def verify_alipay_callback(self, data: dict, signature: str) -> bool:
    # Remove sign fields before verification
    data_copy = data.copy()
    if 'sign' in data_copy:
        del data_copy['sign']
    if 'sign_type' in data_copy:
        del data_copy['sign_type']

    return self.alipay.verify(data_copy, signature)
```

**WeChat Pay:**
```python
def verify_wechat_callback(self, xml_data: str) -> Optional[Dict]:
    # Parse and verify XML callback
    result = self.wechat.parse_payment_result(xml_data)
    return result  # Returns None if verification fails
```

### Order Status Update

```python
def process_payment_success(
    self,
    order_no: str,
    transaction_id: str = None,
    payment_data: Dict = None
) -> Order:
    order = self.get_order_by_no(order_no)

    if order.status == Order.STATUS_PAID:
        # Already paid, return existing order (idempotent)
        return order

    # Mark order as paid (updates status, paid_at, expires_at)
    order.mark_as_paid(transaction_id=transaction_id)
    self.db.commit()
    self.db.refresh(order)

    return order
```

---

## Payment Flow Diagrams

### Alipay Payment Flow

```
User → Frontend: Click "立即购买"
Frontend → Backend: POST /api/v1/subscriptions/orders {plan_id: 2, payment_method: "alipay"}
Backend → Frontend: {order_no: "IDL...", ...}
Frontend → Backend: POST /api/v1/payments/initiate {order_no, payment_method: "alipay"}
Backend → Frontend: {payment_url: "https://openapi.alipay.com/..."}
Frontend → User: Redirect to payment_url
User → Alipay: Complete payment
Alipay → Backend: POST /api/v1/payments/alipay/notify
Backend → Alipay: "success"
Alipay → User: Return to return_url
User → Frontend: View subscription activated
```

### WeChat Pay Native Flow

```
User → Frontend: Click "立即购买"
Frontend → Backend: POST /api/v1/subscriptions/orders {plan_id: 2, payment_method: "wechat"}
Backend → Frontend: {order_no: "IDL...", ...}
Frontend → Backend: POST /api/v1/payments/initiate {order_no, payment_method: "wechat"}
Backend → Frontend: {code_url: "weixin://wxpay/..."}
Frontend → User: Display QR code (code_url)
User → WeChat App: Scan QR code and pay
WeChat → Backend: POST /api/v1/payments/wechat/notify (XML)
Backend → WeChat: XML response with SUCCESS
Frontend → Backend: GET /api/v1/payments/orders/{order_no}/status (polling)
Backend → Frontend: {status: "paid", paid: true}
Frontend → User: View subscription activated
```

---

## Security Considerations

### 1. Signature Verification
- **必须验证所有回调签名**
- Alipay使用RSA2签名
- WeChat Pay使用MD5签名
- 签名验证失败直接返回fail

### 2. Idempotent Callback Handling
- 支付网关可能重复发送回调
- process_payment_success()实现幂等性
- 已支付订单不会重复处理

### 3. HTTPS Required
- 回调URL必须使用HTTPS（生产环境）
- 防止中间人攻击

### 4. Order Amount Verification
- 回调中验证金额是否匹配订单金额（可选增强）

### 5. IP Whitelist (Optional)
- 可配置只接受支付网关IP的回调

---

## Testing

### Sandbox Environment Setup

**Alipay Sandbox:**
1. 注册沙箱账号: https://openhome.alipay.com/develop/sandbox/app
2. 获取沙箱APPID
3. 生成RSA2密钥对
4. 配置.env:
```env
ALIPAY_APPID=沙箱APPID
ALIPAY_PRIVATE_KEY=路径/to/private_key.pem
ALIPAY_PUBLIC_KEY=路径/to/alipay_public_key.pem
ALIPAY_DEBUG=true
```

**WeChat Pay Sandbox:**
1. 申请微信支付测试号
2. 获取商户号和API密钥
3. 下载证书文件
4. 配置.env:
```env
WECHAT_APPID=测试APPID
WECHAT_MCH_ID=测试商户号
WECHAT_API_KEY=测试密钥
WECHAT_APICLIENT_CERT=路径/to/apiclient_cert.pem
WECHAT_APICLIENT_KEY=路径/to/apiclient_key.pem
```

### Testing Callback Locally

**使用ngrok暴露本地回调URL:**
```bash
ngrok http 8000
```

**更新配置中的notify_url:**
```env
ALIPAY_NOTIFY_URL=https://abc123.ngrok.io/api/v1/payments/alipay/notify
WECHAT_NOTIFY_URL=https://abc123.ngrok.io/api/v1/payments/wechat/notify
```

### Manual Testing Steps

1. **创建订单:**
```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/orders \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": 2, "payment_method": "alipay"}'
```

2. **发起支付:**
```bash
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"order_no": "IDL20260119123456ABCD", "payment_method": "alipay"}'
```

3. **打开payment_url完成支付**

4. **查询支付状态:**
```bash
curl -X GET http://localhost:8000/api/v1/payments/orders/IDL20260119123456ABCD/status \
  -H "Authorization: Bearer {token}"
```

---

## Integration Points

### 与Story 7.1集成（订阅计划）
- 使用Order模型存储支付信息
- 支付成功后更新订单状态和过期时间
- 订单金额从SubscriptionPlan获取

### 与Future Story集成
- **Story 7.5:** 支付成功后激活订阅权限
- **Story 7.6:** 退款处理（Alipay/WeChat refund API）

---

## Known Limitations

### MVP阶段限制
- ✅ 支持支付宝网页支付
- ✅ 支持微信支付Native（扫码）
- ⏳ 不支持移动端SDK支付
- ⏳ 不支持支付宝APP支付
- ⏳ 不支持微信支付APP/H5
- ⏳ 退款功能待Story 7.6实现

### 生产环境需求
- 需申请企业支付宝商家账号
- 需申请微信支付商户号
- 需配置HTTPS域名
- 需备案回调URL

---

## Next Steps

### Story 7.3: Apple IAP集成
- 集成Apple StoreKit
- Receipt验证
- 自动续费处理

### Story 7.4: Google Play Billing集成
- 集成Google Play Billing Library
- Purchase验证
- 订阅管理

### Story 7.5: 订阅激活与权限管理
- 支付成功后自动激活订阅
- 权限中间件验证
- 配额自动切换

### Story 7.6: 订阅管理与退款处理
- 退款API集成
- 退款工单系统
- 自动取消订阅

---

## Status

**✅ Story 7.2 完成 (2026-01-19)**

Backend Implementation: ✅ 完成
- Payment Configuration: ✅
- PaymentService: ✅
- Payment Router: ✅
- Callback Handlers: ✅
- SubscriptionService Integration: ✅

Payment Gateway Integration: ✅ 完成
- Alipay SDK: ✅
- WeChat Pay SDK: ✅
- Signature Verification: ✅
- Order Status Update: ✅

Testing: ⏳ 待测试
- Sandbox Testing: ⏳ 需配置沙箱账号
- Callback Testing: ⏳ 需ngrok暴露本地URL
- Production Testing: ⏳ 需企业资质

Frontend Implementation: ⏳ 待开发（不在7.2范围）
- Payment Initiation UI: ⏳
- QR Code Display: ⏳
- Payment Status Polling: ⏳

Documentation: ✅ 完成
