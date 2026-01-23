# idol_private 开发环境搭建指南

## 快速开始（5分钟启动）

### 1. 启动 Docker 服务（PostgreSQL + Redis）

```bash
docker-compose up -d
```

验证服务运行：
```bash
docker-compose ps
# 应该看到 idol_postgres 和 idol_redis 两个容器在运行
```

### 2. 初始化数据库

```bash
cd backend/scripts
./init_db.sh
```

或者手动执行：
```bash
PGPASSWORD=dev_password psql -h localhost -U idol_user -d idol_db -f backend/scripts/init_db.sql
```

### 3. 启动后端服务

```bash
cd backend

# 创建 Python 虚拟环境（首次）
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖（首次）
pip install -r requirements.txt

# 启动 FastAPI 服务
uvicorn app.main:app --reload --port 8000
```

后端 API 文档：http://localhost:8000/docs

### 4. 启动前端应用

```bash
# 在项目根目录

# 安装 Flutter 依赖（首次）
flutter pub get

# 运行应用
flutter run -d chrome  # Web 版本
# 或
flutter run           # 自动检测设备
```

---

## 测试注册流程

1. 启动后端服务（步骤 3）
2. 启动前端应用（步骤 4）
3. 在前端注册页面：
   - 输入手机号（如：13800138000）
   - 点击"发送验证码"
   - 查看后端控制台，会显示生成的验证码
   - 输入验证码和密码
   - 点击"注册"
4. 查看 PostgreSQL 数据库验证用户创建成功：

```bash
PGPASSWORD=dev_password psql -h localhost -U idol_user -d idol_db -c "SELECT * FROM users;"
```

---

## 常见问题排查

### Docker 服务无法启动

```bash
# 检查 Docker Desktop 是否运行
docker --version

# 查看日志
docker-compose logs postgres
docker-compose logs redis

# 重启服务
docker-compose restart
```

### 数据库连接失败

```bash
# 测试 PostgreSQL 连接
PGPASSWORD=dev_password psql -h localhost -U idol_user -d idol_db -c "SELECT 1;"

# 重新初始化数据库
docker-compose down -v  # 删除数据卷
docker-compose up -d
cd backend/scripts && ./init_db.sh
```

### Flutter 依赖安装失败

```bash
# 清理缓存
flutter clean
flutter pub cache repair

# 重新安装
flutter pub get
```

### Python 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 清理虚拟环境重装
deactivate
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 后端启动报错 "ModuleNotFoundError"

确保：
1. 虚拟环境已激活：`source venv/bin/activate`
2. 在 backend/ 目录下运行 uvicorn
3. 依赖已安装：`pip install -r requirements.txt`

---

## 开发工具推荐

- **API 测试**：访问 http://localhost:8000/docs (Swagger UI)
- **数据库管理**：
  - TablePlus
  - pgAdmin
  - DBeaver
- **Redis 管理**：
  - RedisInsight
  - Redis Commander
- **Flutter 开发**：
  - VS Code + Flutter 扩展
  - Android Studio

---

## 项目结构

```
idol_private/
├── lib/                          # Flutter 前端
│   ├── main.dart                 # 应用入口（已集成 Riverpod）
│   └── features/auth/            # 认证模块
│       ├── models/user.dart      # User 数据模型
│       ├── services/auth_service.dart  # API 调用服务
│       ├── providers/auth_provider.dart  # Riverpod 状态管理
│       └── screens/register_screen.dart  # 注册页面
│
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── main.py               # FastAPI 入口（已注册路由）
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── models/user.py        # User ORM 模型
│   │   ├── schemas/auth.py       # Pydantic schemas
│   │   ├── routers/auth.py       # 认证 API 端点
│   │   ├── services/sms_service.py  # 验证码服务
│   │   └── core/security.py      # 密码哈希 + JWT
│   ├── scripts/
│   │   ├── init_db.sql           # 数据库初始化 SQL
│   │   └── init_db.sh            # 数据库初始化脚本
│   ├── requirements.txt          # Python 依赖
│   ├── .env                      # 环境变量（已生成密钥）
│   └── .env.example              # 环境变量模板
│
├── docker-compose.yml            # Docker 服务配置
├── README.md                     # 项目说明
└── SETUP.md                      # 本文档
```

---

## API 端点

### 认证相关

- `POST /api/v1/auth/send-code` - 发送验证码
  ```json
  Request: {"phone": "13800138000"}
  Response: {"message": "验证码已发送", "expires_in": 300}
  ```

- `POST /api/v1/auth/register` - 用户注册
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

- `GET /health` - 健康检查
  ```json
  Response: {"status": "ok"}
  ```

完整 API 文档：http://localhost:8000/docs

---

## 下一步开发

- [ ] 实现用户登录功能（Story 1.2）
- [ ] 实现密码重置功能（Story 1.3）
- [ ] 实现 Material Design 3 主题（Story 1.4）
- [ ] 创建偶像数据模型和配置（Story 1.5）

---

## 安全注意事项

⚠️ **重要提示**：

1. **.env 文件已添加到 .gitignore**，绝不提交到 Git
2. **生产环境必须重新生成密钥**：
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
3. **CORS 配置**：生产环境必须限制 `allow_origins`
4. **JWT 过期时间**：当前为 7 天，符合架构要求

---

**祝开发顺利！🎉**
