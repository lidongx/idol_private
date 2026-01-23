# Story 1.1: 项目初始化与用户注册

Status: ready-for-dev

> **📝 本Story合并了原Epic 0的项目初始化工作**
> **⏱️ 预估时间:** 2-3天（Day 1: 项目搭建，Day 2-3: 注册功能）

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **开发团队**,
I want **初始化完整的项目结构并实现用户注册功能**,
so that **新用户可以通过手机号注册账号，为后续所有功能建立技术基础**。

## Acceptance Criteria

### Part A: 项目初始化 (Day 1)

**AC1.1: 项目目录结构创建**
- **Given** 一个空白Git仓库
- **When** 初始化项目结构
- **Then** 创建以下目录结构：
```
idol_private/
├── frontend/          # Flutter项目
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app/       # 应用配置
│   │   ├── routes/    # 路由管理
│   │   ├── models/    # 数据模型
│   │   ├── services/  # 业务服务
│   │   ├── widgets/   # 通用组件
│   │   └── features/  # 功能模块
│   │       └── auth/  # 认证模块
│   ├── pubspec.yaml
│   └── analysis_options.yaml
├── backend/           # FastAPI项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/    # SQLAlchemy模型
│   │   ├── routers/   # API路由
│   │   │   └── auth.py
│   │   ├── services/  # 业务逻辑
│   │   └── utils/     # 工具函数
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml # 本地PostgreSQL+Redis
├── .gitignore
└── README.md
```

**AC1.2: Flutter依赖配置完成**
- **Given** Flutter项目已初始化
- **When** 配置`pubspec.yaml`
- **Then** 包含以下依赖：
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_secure_storage: ^9.0.0  # Token安全存储
  http: ^1.2.2                    # HTTP客户端
  riverpod: ^2.6.1                # 状态管理 (Architecture要求)
```

**AC1.3: FastAPI依赖配置完成**
- **Given** Backend目录已创建
- **When** 配置`requirements.txt`
- **Then** 包含以下依赖（版本符合Architecture规范）：
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
pydantic==2.9.0
pydantic-settings==2.6.0
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # 密码哈希
python-multipart==0.0.6
redis==5.0.1
```

**AC1.4: Docker Compose本地开发环境**
- **Given** docker-compose.yml已创建
- **When** 运行`docker-compose up -d`
- **Then** 启动以下服务：
  - PostgreSQL 15-alpine (端口5432)
  - Redis 7-alpine (端口6379)
- **And** PostgreSQL自动创建数据库`idol_db`
- **And** 数据持久化到Docker volumes

**AC1.5: 后端健康检查通过**
- **Given** FastAPI应用已启动
- **When** 访问`GET /health`
- **Then** 返回`{"status": "ok"}`
- **And** 响应时间 < 100ms

**AC1.6: Flutter应用可运行**
- **Given** Flutter依赖已安装
- **When** 运行`flutter run`
- **Then** 显示默认Welcome界面或登录/注册界面占位符
- **And** 无编译错误

---

### Part B: 用户注册功能 (Day 2-3)

**AC2.1: 手机号验证码注册流程**
- **Given** 用户在注册页面
- **When** 用户输入手机号（中国大陆11位格式）
- **Then** 系统验证手机号格式
- **And** 调用`POST /api/v1/auth/send-code`发送6位数验证码
- **And** 验证码存储在Redis：key=`sms:verify:{phone}`, TTL=300秒
- **And** 前端显示验证码输入框和60秒倒计时

**AC2.2: 用户注册完成**
- **Given** 用户已收到验证码
- **When** 用户输入验证码+密码（至少8位，包含字母和数字）
- **And** 点击"注册"按钮
- **Then** 调用`POST /api/v1/auth/register`
- **And** 后端验证验证码正确性（Redis中匹配）
- **And** 密码使用bcrypt哈希存储（cost factor = 12）
- **And** 创建users表记录
- **And** 生成JWT Token（有效期7天）
- **And** 返回Token给前端
- **And** 前端将Token存储到`flutter_secure_storage`
- **And** 自动登录并跳转到偶像介绍页

**AC2.3: Users数据库表创建**
- **Given** PostgreSQL数据库连接正常
- **When** 执行数据库迁移脚本
- **Then** 创建users表：
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(11) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_phone ON users(phone);
```

**AC2.4: API端点实现完成**
- **Given** FastAPI路由已配置
- **When** 后端启动
- **Then** 以下端点可访问：
  - `POST /api/v1/auth/send-code` - 发送验证码
  - `POST /api/v1/auth/register` - 用户注册
  - `GET /health` - 健康检查

**AC2.5: Flutter注册页面实现**
- **Given** Flutter项目已运行
- **When** 用户导航到注册页面
- **Then** 以下文件已创建并集成：
  - `lib/features/auth/screens/register_screen.dart` - 注册UI
  - `lib/features/auth/services/auth_service.dart` - API调用服务
  - `lib/features/auth/models/user.dart` - 用户数据模型

**AC2.6: Edge Cases处理**
- 手机号已注册 → 返回400错误："该手机号已注册，请直接登录"
- 验证码错误 → 返回400错误："验证码错误，请重新输入"（最多尝试3次）
- 验证码过期 → 返回400错误："验证码已过期，请重新发送"
- 数据库连接失败 → 返回500错误："服务暂时不可用，请稍后重试"
- 密码强度不足 → 前端拦截并提示："密码至少8位，需包含字母和数字"

---

## Tasks / Subtasks

### Phase 1: 项目基础搭建 (Day 1, 6-8小时)

- [ ] **Task 1.1: 初始化Git仓库和目录结构** (AC: 1.1)
  - [ ] 1.1.1 创建idol_private目录并初始化Git
  - [ ] 1.1.2 创建frontend/和backend/顶层目录
  - [ ] 1.1.3 配置.gitignore（排除.env, venv/, node_modules/, .flutter-plugins等）
  - [ ] 1.1.4 创建README.md说明项目结构和启动步骤

- [ ] **Task 1.2: 初始化Flutter项目** (AC: 1.2, 1.6)
  - [ ] 1.2.1 运行`flutter create --org com.idolprivate --platforms android,ios,web frontend`
  - [ ] 1.2.2 在frontend/lib/下创建features/, models/, services/, widgets/目录
  - [ ] 1.2.3 在frontend/lib/features/下创建auth/子目录
  - [ ] 1.2.4 配置pubspec.yaml添加flutter_secure_storage, http, riverpod依赖
  - [ ] 1.2.5 运行`flutter pub get`安装依赖
  - [ ] 1.2.6 运行`flutter run`验证项目可启动

- [ ] **Task 1.3: 初始化FastAPI后端结构** (AC: 1.3, 1.5)
  - [ ] 1.3.1 创建backend/app/目录结构（models/, routers/, services/, utils/）
  - [ ] 1.3.2 创建backend/app/main.py（FastAPI应用入口，含CORS配置）
  - [ ] 1.3.3 创建backend/app/config.py（Pydantic Settings环境变量管理）
  - [ ] 1.3.4 创建backend/app/database.py（SQLAlchemy连接和session管理）
  - [ ] 1.3.5 创建backend/requirements.txt（按Architecture指定版本）
  - [ ] 1.3.6 创建Python虚拟环境并安装依赖：
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
  - [ ] 1.3.7 实现GET /health端点返回{"status": "ok"}
  - [ ] 1.3.8 运行`uvicorn app.main:app --reload`验证启动成功

- [ ] **Task 1.4: 配置Docker Compose本地开发环境** (AC: 1.4)
  - [ ] 1.4.1 创建docker-compose.yml配置PostgreSQL 15-alpine服务
  - [ ] 1.4.2 配置postgres环境变量（POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD）
  - [ ] 1.4.3 添加Redis 7-alpine服务到docker-compose.yml
  - [ ] 1.4.4 配置Docker volumes持久化（postgres_data, redis_data）
  - [ ] 1.4.5 创建backend/.env.example模板文件
  - [ ] 1.4.6 创建backend/.env文件（gitignored）：
    ```bash
    DATABASE_URL=postgresql://idol_user:dev_password@localhost:5432/idol_db
    REDIS_URL=redis://localhost:6379/0
    SECRET_KEY=<生成随机密钥>
    JWT_SECRET_KEY=<生成随机密钥>
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天
    ```
  - [ ] 1.4.7 运行`docker-compose up -d`启动服务
  - [ ] 1.4.8 验证PostgreSQL连接：`psql -h localhost -U idol_user -d idol_db`
  - [ ] 1.4.9 验证Redis连接：`redis-cli ping`

### Phase 2: 用户注册后端实现 (Day 2, 8小时)

- [ ] **Task 2.1: 创建Users数据模型** (AC: 2.3)
  - [ ] 2.1.1 创建backend/app/models/user.py（SQLAlchemy User模型）
  - [ ] 2.1.2 定义字段：id, phone, password_hash, subscription_tier, subscription_expires_at, created_at, updated_at
  - [ ] 2.1.3 添加phone字段unique约束和索引
  - [ ] 2.1.4 创建Alembic迁移脚本（可选，MVP阶段可手动建表）
  - [ ] 2.1.5 运行SQL创建users表

- [ ] **Task 2.2: 实现密码哈希和JWT工具** (AC: 2.2)
  - [ ] 2.2.1 创建backend/app/core/security.py
  - [ ] 2.2.2 实现password hashing函数（使用passlib bcrypt, rounds=12）:
    ```python
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def hash_password(password: str) -> str
    def verify_password(plain_password: str, hashed_password: str) -> bool
    ```
  - [ ] 2.2.3 实现JWT token生成函数（使用python-jose）:
    ```python
    from jose import jwt
    def create_access_token(data: dict, expires_delta: timedelta) -> str
    def decode_access_token(token: str) -> dict
    ```
  - [ ] 2.2.4 配置JWT算法为HS256，过期时间7天

- [ ] **Task 2.3: 实现验证码发送逻辑** (AC: 2.1)
  - [ ] 2.3.1 创建backend/app/services/sms_service.py
  - [ ] 2.3.2 实现generate_verification_code()生成6位随机数字
  - [ ] 2.3.3 实现store_code_in_redis(phone, code)，TTL=300秒
  - [ ] 2.3.4 实现verify_code_from_redis(phone, code) → bool
  - [ ] 2.3.5 MVP阶段：send_sms_code()使用console.log mock（生产环境替换为阿里云SMS）
  - [ ] 2.3.6 添加重发限制：同一手机号60秒内只能发送一次

- [ ] **Task 2.4: 实现注册API端点** (AC: 2.1, 2.2, 2.4, 2.6)
  - [ ] 2.4.1 创建backend/app/schemas/auth.py（Pydantic schemas）:
    - SendCodeRequest: phone
    - RegisterRequest: phone, verification_code, password
    - TokenResponse: access_token, token_type
  - [ ] 2.4.2 创建backend/app/routers/auth.py
  - [ ] 2.4.3 实现POST /api/v1/auth/send-code端点：
    - 验证手机号格式（11位数字，1开头）
    - 生成6位验证码
    - 存储到Redis（key: sms:verify:{phone}, TTL: 300秒）
    - 调用SMS服务发送（MVP用console.log）
    - 返回success消息
  - [ ] 2.4.4 实现POST /api/v1/auth/register端点：
    - 验证手机号格式
    - 从Redis验证验证码正确性
    - 验证密码强度（>=8位，含字母和数字）
    - 检查手机号是否已注册（查询users表）
    - 哈希密码（bcrypt, rounds=12）
    - 创建users记录（subscription_tier='free'）
    - 生成JWT token
    - 返回TokenResponse
  - [ ] 2.4.5 实现错误处理（AC 2.6）:
    - 400: 手机号已注册/验证码错误/验证码过期/密码强度不足
    - 500: 数据库连接失败
  - [ ] 2.4.6 在app/main.py中注册auth路由：`app.include_router(auth.router, prefix="/api/v1/auth")`

- [ ] **Task 2.5: 配置CORS和环境变量** (AC: 1.5, 2.2)
  - [ ] 2.5.1 在backend/app/main.py配置CORS middleware（允许Flutter Web调用）:
    ```python
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # MVP阶段，生产环境需限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```
  - [ ] 2.5.2 从.env加载环境变量（使用Pydantic Settings）
  - [ ] 2.5.3 验证DATABASE_URL、REDIS_URL、JWT_SECRET_KEY正确加载

### Phase 3: Flutter注册前端实现 (Day 3, 8小时)

- [ ] **Task 3.1: 创建User数据模型** (AC: 2.5)
  - [ ] 3.1.1 创建frontend/lib/features/auth/models/user.dart
  - [ ] 3.1.2 定义User类：id, phone, subscriptionTier, createdAt
  - [ ] 3.1.3 实现fromJson和toJson方法

- [ ] **Task 3.2: 实现AuthService API调用** (AC: 2.1, 2.2, 2.5)
  - [ ] 3.2.1 创建frontend/lib/features/auth/services/auth_service.dart
  - [ ] 3.2.2 实现sendVerificationCode(String phone) → Future<bool>
    - POST http://localhost:8000/api/v1/auth/send-code
    - 返回成功/失败状态
  - [ ] 3.2.3 实现register(String phone, String code, String password) → Future<String>
    - POST http://localhost:8000/api/v1/auth/register
    - 返回JWT token字符串
  - [ ] 3.2.4 实现saveToken(String token)使用flutter_secure_storage
  - [ ] 3.2.5 实现getToken() → Future<String?>读取存储的token
  - [ ] 3.2.6 添加错误处理：网络超时、400/500错误码解析

- [ ] **Task 3.3: 实现注册页面UI** (AC: 2.1, 2.2, 2.5)
  - [ ] 3.3.1 创建frontend/lib/features/auth/screens/register_screen.dart
  - [ ] 3.3.2 使用Material Design 3组件（TextField, ElevatedButton, Text）
  - [ ] 3.3.3 实现手机号输入框（限制11位数字，键盘类型phone）
  - [ ] 3.3.4 实现"发送验证码"按钮（带60秒倒计时禁用逻辑）
  - [ ] 3.3.5 实现验证码输入框（6位数字）
  - [ ] 3.3.6 实现密码输入框（obscureText=true，显示/隐藏切换）
  - [ ] 3.3.7 实现密码确认输入框
  - [ ] 3.3.8 实现前端验证：
    - 手机号格式（11位，1开头）
    - 密码强度（>=8位，含字母和数字）
    - 两次密码一致性
  - [ ] 3.3.9 实现"注册"按钮调用AuthService.register()
  - [ ] 3.3.10 注册成功后自动跳转到偶像介绍页（Navigator.pushReplacement）

- [ ] **Task 3.4: 集成Riverpod状态管理** (AC: 1.2)
  - [ ] 3.4.1 在frontend/lib/main.dart中添加ProviderScope wrapper
  - [ ] 3.4.2 创建frontend/lib/features/auth/providers/auth_provider.dart
  - [ ] 3.4.3 定义authServiceProvider（提供AuthService实例）
  - [ ] 3.4.4 定义userProvider（管理当前用户状态）
  - [ ] 3.4.5 在RegisterScreen中使用ref.watch/ref.read访问providers

- [ ] **Task 3.5: 添加Loading和Error UI状态** (AC: 2.5, 2.6)
  - [ ] 3.5.1 在注册过程中显示CircularProgressIndicator
  - [ ] 3.5.2 使用SnackBar显示错误消息（手机号已注册、验证码错误等）
  - [ ] 3.5.3 网络请求失败时显示友好提示："网络连接失败，请检查网络后重试"

### Phase 4: 集成测试与部署准备 (Day 3, 2小时)

- [ ] **Task 4.1: 端到端注册流程测试** (AC: 所有)
  - [ ] 4.1.1 启动docker-compose（PostgreSQL + Redis）
  - [ ] 4.1.2 启动FastAPI后端（uvicorn app.main:app --reload）
  - [ ] 4.1.3 启动Flutter前端（flutter run）
  - [ ] 4.1.4 手动测试完整注册流程：
    - 输入手机号 → 发送验证码 → 检查控制台验证码
    - 输入验证码+密码 → 点击注册
    - 验证users表中新增记录
    - 验证JWT token存储到flutter_secure_storage
    - 验证自动跳转到偶像介绍页
  - [ ] 4.1.5 测试Edge Cases（手机号已注册、验证码错误、密码弱等）

- [ ] **Task 4.2: 编写API自动化测试** (可选，时间允许)
  - [ ] 4.2.1 创建backend/tests/test_auth.py
  - [ ] 4.2.2 使用pytest编写/auth/send-code端点测试
  - [ ] 4.2.3 使用pytest编写/auth/register端点测试
  - [ ] 4.2.4 Mock Redis和数据库依赖
  - [ ] 4.2.5 运行`pytest tests/test_auth.py`验证通过

- [ ] **Task 4.3: 文档更新** (AC: 1.1)
  - [ ] 4.3.1 更新README.md添加：
    - 项目启动步骤（docker-compose, backend, frontend）
    - 环境变量配置说明
    - API端点文档链接（/docs）
  - [ ] 4.3.2 创建backend/.env.example模板供团队使用
  - [ ] 4.3.3 添加troubleshooting常见问题（数据库连接失败、Flutter依赖安装等）

---

## Dev Notes

### 🏗️ 架构模式和约束

#### **1. Technology Stack (严格遵循Architecture规范)**

**Frontend:**
- Flutter SDK >= 3.0.0
- 状态管理: **Riverpod 2.6.1+** (非Provider! Architecture明确要求)
- HTTP客户端: http ^1.2.2
- 安全存储: flutter_secure_storage ^9.0.0
- UI系统: Material Design 3

**Backend:**
- FastAPI 0.115.0 + Uvicorn 0.32.0
- Python 3.11+
- SQLAlchemy 2.0.35 (ORM)
- Pydantic 2.9.0 + Pydantic Settings 2.6.0
- python-jose[cryptography] 3.3.0 (JWT)
- passlib[bcrypt] 1.7.4 (密码哈希)

**Infrastructure:**
- PostgreSQL 15+ (用户数据)
- Redis 7+ (验证码临时存储)
- Docker Compose (本地开发环境)

---

#### **2. 项目结构 (Hybrid Monorepo)**

```
idol_private/
├── frontend/                    # Flutter应用
│   ├── lib/
│   │   ├── main.dart            # 应用入口（含ProviderScope）
│   │   ├── features/            # Feature-first组织
│   │   │   └── auth/
│   │   │       ├── models/      # user.dart
│   │   │       ├── screens/     # register_screen.dart
│   │   │       ├── services/    # auth_service.dart
│   │   │       └── providers/   # auth_provider.dart
│   │   ├── core/                # 核心配置
│   │   ├── shared/              # 共享组件
│   │   └── config/
│   ├── test/
│   ├── pubspec.yaml
│   └── README.md
│
├── backend/                     # FastAPI应用
│   ├── app/
│   │   ├── main.py              # FastAPI入口 + CORS配置
│   │   ├── config.py            # Pydantic Settings环境变量
│   │   ├── database.py          # SQLAlchemy连接和session
│   │   ├── models/
│   │   │   └── user.py          # User SQLAlchemy模型
│   │   ├── schemas/
│   │   │   └── auth.py          # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   └── auth.py          # /api/v1/auth/* 端点
│   │   ├── services/
│   │   │   └── sms_service.py   # 验证码生成和Redis存储
│   │   ├── core/
│   │   │   └── security.py      # bcrypt + JWT工具函数
│   │   └── utils/
│   ├── tests/
│   │   └── test_auth.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── docker-compose.yml           # PostgreSQL + Redis服务
├── .gitignore
└── README.md
```

**命名约定:**
- Flutter: `lowercase_with_underscores.dart`
- Python: `snake_case.py`（文件名）, `PascalCase`（类名）
- Organization ID: `com.idolprivate`

---

#### **3. API设计模式**

**RESTful API规范:**
- Base URL: `/api/v1/`
- 版本控制: Path-based versioning
- 文档: Swagger UI at `/docs`, ReDoc at `/redoc`

**认证流程 (Story 1.1 Part B):**
1. `POST /api/v1/auth/send-code`
   ```json
   Request: {"phone": "13800138000"}
   Response: {"message": "验证码已发送", "expires_in": 300}
   ```

2. `POST /api/v1/auth/register`
   ```json
   Request: {
     "phone": "13800138000",
     "verification_code": "123456",
     "password": "Pass1234"
   }
   Response: {
     "access_token": "eyJ...",
     "token_type": "bearer"
   }
   ```

3. JWT存储: Flutter uses `flutter_secure_storage` (Keychain/KeyStore)
4. Token验证: `Authorization: Bearer <token>` header

**错误响应格式:**
```json
{
  "detail": "该手机号已注册",
  "error_code": "USER_ALREADY_EXISTS"
}
```

**CORS配置 (MVP阶段):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### **4. 数据库Schema**

**Users表设计:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(11) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_phone ON users(phone);
```

**SQLAlchemy模型 (backend/app/models/user.py):**
```python
from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    subscription_tier = Column(String(20), default="free")
    subscription_expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
```

**Redis验证码存储:**
- Key format: `sms:verify:{phone}`
- Value: 6位数字验证码
- TTL: 300秒（5分钟）
- 重发限制: 同一手机号60秒内只能发送一次（key: `sms:ratelimit:{phone}`, TTL: 60秒）

---

#### **5. 安全要求 (CRITICAL)**

**密码哈希 (bcrypt):**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 哈希密码（注册时）
hashed_password = pwd_context.hash(plain_password)  # rounds=12 default

# 验证密码（登录时）
is_valid = pwd_context.verify(plain_password, hashed_password)
```

**JWT配置 (backend/app/core/security.py):**
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 随机生成，保密
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7天 (Architecture要求: ≤7天)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**环境变量管理 (.env文件):**
```bash
# 数据库
DATABASE_URL=postgresql://idol_user:dev_password@localhost:5432/idol_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT密钥（必须随机生成，保密！）
SECRET_KEY=随机生成的32位字符串
JWT_SECRET_KEY=随机生成的32位字符串
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# SMS服务（生产环境使用阿里云SMS）
SMS_PROVIDER=console  # MVP阶段用console.log，生产环境改为aliyun
ALIYUN_SMS_ACCESS_KEY_ID=
ALIYUN_SMS_ACCESS_KEY_SECRET=
ALIYUN_SMS_SIGN_NAME=
ALIYUN_SMS_TEMPLATE_CODE=
```

**Transport Layer Security:**
- 生产环境必须使用HTTPS TLS 1.2+
- 本地开发可使用HTTP（仅限localhost）

---

#### **6. 开发环境配置**

**Docker Compose (docker-compose.yml):**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: idol_db
      POSTGRES_USER: idol_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**启动命令:**
```bash
# 1. 启动Docker服务
docker-compose up -d

# 2. 启动FastAPI后端（在backend/目录）
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 3. 启动Flutter前端（在frontend/目录）
flutter pub get
flutter run
```

**环境初始化脚本 (scripts/init-dev.sh):**
```bash
#!/bin/bash
# 自动化环境搭建脚本

# 检查Python 3.11+
python3.11 --version || (echo "需要Python 3.11+" && exit 1)

# 检查Flutter SDK
flutter --version || (echo "需要安装Flutter SDK" && exit 1)

# 检查Docker
docker --version || (echo "需要安装Docker" && exit 1)

# 后端环境
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 前端环境
cd frontend
flutter pub get
cd ..

# 启动Docker
docker-compose up -d

echo "✅ 开发环境初始化完成！"
echo "Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "Frontend: cd frontend && flutter run"
```

---

#### **7. 测试标准**

**测试框架:**
- Frontend: Flutter Test (unit testing), Integration Test (E2E)
- Backend: Pytest + pytest-asyncio (async支持)

**测试覆盖率要求:**
- 关键路径（注册、登录）: 80%+ 代码覆盖率
- Edge cases必须覆盖（手机号已注册、验证码错误等）

**单元测试示例 (backend/tests/test_auth.py):**
```python
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    plain = "TestPass123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) == True
    assert verify_password("WrongPass", hashed) == False

def test_jwt_token_creation():
    data = {"user_id": 1, "phone": "13800138000"}
    token = create_access_token(data)
    assert token is not None
    decoded = decode_access_token(token)
    assert decoded["user_id"] == 1
    assert decoded["phone"] == "13800138000"
```

**测试执行命令:**
```bash
# Backend tests
cd backend
pytest tests/ --cov=app --cov-report=xml

# Frontend tests
cd frontend
flutter test
```

---

### 🚨 CRITICAL IMPLEMENTATION WARNINGS

#### **⚠️ Riverpod vs Provider混淆风险 (HIGH PRIORITY)**
- **Architecture明确要求使用Riverpod 2.6.1+，NOT Provider！**
- epics.md中Story 1.1的Technical Notes错误地写着"Flutter状态管理使用Provider"
- **必须使用Riverpod！** Architecture文档第427行明确规定
- Provider是旧的状态管理方案，已被Riverpod取代
- **Action:** pubspec.yaml中添加`riverpod: ^2.6.1`，NOT `provider`

#### **⚠️ 密码哈希轮数 (SECURITY)**
- bcrypt默认rounds=12（合理平衡安全性和性能）
- 不要使用低于10的rounds（不安全）
- 不要使用高于14的rounds（性能过慢，影响用户体验）

#### **⚠️ JWT过期时间 (ARCHITECTURE CONSTRAINT)**
- Architecture明确要求: ≤ 7天 (NFR-S3)
- epics.md中建议7天过期（10080分钟）
- **不要设置更长的过期时间！** 违反安全规范

#### **⚠️ CORS配置 (SECURITY)**
- MVP阶段`allow_origins=["*"]`可接受
- **生产环境必须限制为特定域名！**
- 例如: `allow_origins=["https://idolprivate.com", "https://app.idolprivate.com"]`

#### **⚠️ 验证码存储 (REDIS KEY PATTERN)**
- **必须使用格式:** `sms:verify:{phone}`
- **TTL必须设置:** 300秒（5分钟）
- **重发限制Key:** `sms:ratelimit:{phone}`, TTL=60秒

#### **⚠️ 环境变量泄露风险 (CRITICAL)**
- .env文件**必须添加到.gitignore**
- SECRET_KEY和JWT_SECRET_KEY**必须随机生成**，不能使用固定值
- 生成方法：`python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **绝不将.env文件提交到Git！**

#### **⚠️ SQLAlchemy 2.0+ 语法变更**
- Architecture使用SQLAlchemy 2.0.35（新版本）
- 必须使用新的2.0语法（`select()`, `insert()`等）
- 旧的1.x查询语法已被弃用
- 参考: https://docs.sqlalchemy.org/en/20/changelog/migration_20.html

#### **⚠️ Flutter Web CORS预检请求**
- Flutter Web应用会发送OPTIONS预检请求
- FastAPI CORS配置必须包含`allow_methods=["*"]`和`allow_headers=["*"]`
- 否则POST /api/v1/auth/register会被浏览器阻止

---

### 📚 技术细节参考

#### **手机号格式验证 (中国大陆)**
- 正则表达式: `^1[3-9]\d{9}$`
- 长度: 11位
- 首位: 1
- 第二位: 3-9（覆盖所有运营商号段）

**Python实现:**
```python
import re

def validate_phone(phone: str) -> bool:
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))
```

**Dart实现:**
```dart
bool validatePhone(String phone) {
  final pattern = RegExp(r'^1[3-9]\d{9}$');
  return pattern.hasMatch(phone);
}
```

---

#### **密码强度验证**
- 最小长度: 8位
- 必须包含: 至少1个字母 + 至少1个数字
- 可选: 特殊字符（提升安全性）

**Python实现:**
```python
import re

def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True
```

**Dart实现:**
```dart
bool validatePassword(String password) {
  if (password.length < 8) return false;
  if (!RegExp(r'[a-zA-Z]').hasMatch(password)) return false;
  if (!RegExp(r'\d').hasMatch(password)) return false;
  return true;
}
```

---

#### **验证码生成算法**
```python
import random

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])
```

---

#### **Redis操作示例 (Python)**
```python
import redis
from datetime import timedelta

redis_client = redis.Redis.from_url("redis://localhost:6379/0")

# 存储验证码
def store_verification_code(phone: str, code: str):
    key = f"sms:verify:{phone}"
    redis_client.setex(key, timedelta(seconds=300), code)

# 验证验证码
def verify_verification_code(phone: str, input_code: str) -> bool:
    key = f"sms:verify:{phone}"
    stored_code = redis_client.get(key)
    if stored_code is None:
        return False  # 验证码已过期
    return stored_code.decode('utf-8') == input_code

# 重发限制检查
def can_resend_code(phone: str) -> bool:
    key = f"sms:ratelimit:{phone}"
    return redis_client.get(key) is None

# 设置重发限制
def set_resend_limit(phone: str):
    key = f"sms:ratelimit:{phone}"
    redis_client.setex(key, timedelta(seconds=60), "1")
```

---

### Project Structure Notes

**✅ 与Architecture规范对齐:**
- Hybrid Monorepo结构（frontend/ + backend/）
- Frontend使用Feature-first组织（features/auth/, features/conversation/等）
- Backend使用Layered Architecture（routers → services → models）
- Separation of Concerns: 严格分离routes, schemas, models, services

**⚠️ 发现的差异:**
1. **Riverpod vs Provider:**
   - epics.md Technical Notes错误提到"Provider"
   - Architecture明确要求Riverpod 2.6.1+
   - **Resolution:** 使用Riverpod（Architecture为准）

2. **验证码实现细节缺失:**
   - Architecture未指定SMS服务提供商
   - epics.md建议阿里云SMS或console.log mock
   - **Resolution:** MVP阶段使用console.log mock，生产环境使用阿里云SMS

3. **数据库迁移工具未指定:**
   - Architecture提到SQLAlchemy 2.0.35但未指定迁移工具
   - **Recommendation:** 使用Alembic（SQLAlchemy官方迁移工具）

---

### References

**Architecture文档:**
- [Technology Stack - Frontend] `/Users/lidong/Desktop/Git/idol_private/_bmad-output/planning-artifacts/architecture.md` Lines 427-450
- [Technology Stack - Backend] `architecture.md` Lines 451-470
- [Database Layer] `architecture.md` Lines 471-490
- [Security Requirements] `architecture.md` Lines 900-950
- [JWT Configuration] `architecture.md` Lines 920-935
- [CORS Configuration] `architecture.md` Lines 850-865
- [Project Structure] `architecture.md` Lines 300-400

**Epics文档:**
- [Epic 1 Overview] `/Users/lidong/Desktop/Git/idol_private/_bmad-output/planning-artifacts/epics.md` Lines 1631-1641
- [Story 1.1 Full Spec] `epics.md` Lines 1644-1806
- [Part A: 项目初始化] `epics.md` Lines 1655-1753
- [Part B: 用户注册功能] `epics.md` Lines 1756-1805

**PRD文档:**
- [FR1-FR7: 账号注册与管理] `/Users/lidong/Desktop/Git/idol_private/_bmad-output/planning-artifacts/prd.md` (FRs 1-7)
- [NFR-S1-S4: 安全需求] `prd.md` (Security NFRs)
- [NFR-09: 3分钟完成首次对话] `prd.md` (Performance NFR)

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

(To be filled during implementation)

### Completion Notes List

(To be filled during implementation)

### File List

**To be created during implementation:**

**Backend Files:**
- `backend/app/main.py` - FastAPI应用入口
- `backend/app/config.py` - Pydantic Settings配置
- `backend/app/database.py` - SQLAlchemy连接管理
- `backend/app/models/user.py` - User ORM模型
- `backend/app/schemas/auth.py` - Pydantic schemas
- `backend/app/routers/auth.py` - 认证API端点
- `backend/app/services/sms_service.py` - 验证码服务
- `backend/app/core/security.py` - bcrypt + JWT工具
- `backend/requirements.txt` - Python依赖
- `backend/.env` - 环境变量（gitignored）
- `backend/.env.example` - 环境变量模板

**Frontend Files:**
- `frontend/lib/main.dart` - Flutter应用入口
- `frontend/lib/features/auth/models/user.dart` - User数据模型
- `frontend/lib/features/auth/services/auth_service.dart` - API调用服务
- `frontend/lib/features/auth/screens/register_screen.dart` - 注册UI
- `frontend/lib/features/auth/providers/auth_provider.dart` - Riverpod providers
- `frontend/pubspec.yaml` - Flutter依赖

**Infrastructure Files:**
- `docker-compose.yml` - PostgreSQL + Redis配置
- `.gitignore` - Git忽略规则
- `README.md` - 项目文档和启动指南
- `scripts/init-dev.sh` - 自动化环境搭建脚本

**Database:**
- `users` table (created via SQL or Alembic migration)

---

## 🎯 Implementation Success Criteria

**Story完成标准:**
- ✅ 所有Acceptance Criteria通过验证
- ✅ docker-compose up成功启动PostgreSQL + Redis
- ✅ FastAPI后端启动并通过GET /health健康检查
- ✅ Flutter前端成功运行并显示注册界面
- ✅ 完整注册流程测试通过（手机号 → 验证码 → 注册 → JWT存储 → 跳转）
- ✅ Edge Cases全部处理（手机号已注册、验证码错误、密码弱等）
- ✅ users表成功创建并能查询到新注册用户
- ✅ JWT token正确生成并存储到flutter_secure_storage
- ✅ 代码符合Architecture规范（Riverpod状态管理、bcrypt密码哈希、JWT过期时间≤7天）
- ✅ README.md文档更新，包含启动步骤和环境配置说明

**Definition of Done:**
- 代码已提交到Git仓库（.env文件excluded）
- 至少1个手动端到端测试通过
- 无已知critical bugs
- 文档（README.md）更新完成

---

**🚀 Ready for Dev Agent Implementation!**

开发人员现在拥有完整的上下文和实施指南，可以无阻碍地开始Story 1.1的开发工作。所有架构约束、安全要求、技术细节、Edge Cases处理方法均已明确定义。
