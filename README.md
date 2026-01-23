# idol_private - AI虚拟偶像情感陪伴应用

> "你的专属AI恋人，24小时懂你的心"

## 项目简介

idol_private 是一款AI驱动的虚拟偶像情感陪伴应用，结合VTuber的人情味和AI的24小时可用性，为用户提供真实、温暖的情感陪伴体验。

### 核心特性

- 🎭 **AI版VTuber** - 真实偶像人设（情绪+生活节奏）
- 💬 **人情味对话引擎** - 口语化、有情绪、不完美
- ❤️ **亲密度养成系统** - Lv1-100成长体系
- 🔄 **反向陪伴机制** - 双向情感连接
- ⏰ **每日仪式** - 早安+运势+晚安

## 技术栈

### Frontend
- **Flutter** 3.x - 跨平台移动应用框架 (Android + iOS + Web)
- **Riverpod** 2.6.1+ - 状态管理
- **Material Design 3** - UI设计系统

### Backend
- **FastAPI** 0.115.0 - 现代Python Web框架
- **Python** 3.11+
- **SQLAlchemy** 2.0.35 - ORM
- **PostgreSQL** 15+ - 关系型数据库
- **Redis** 7+ - 缓存和会话存储

## 项目结构

```
idol_private/
├── lib/                      # Flutter前端代码
│   ├── main.dart
│   └── features/             # 功能模块（待创建）
│       └── auth/             # 认证模块
├── backend/                  # FastAPI后端（待创建）
│   ├── app/
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml        # Docker服务配置（待创建）
├── pubspec.yaml              # Flutter依赖
└── README.md
```

## 快速开始

### 前置要求

- **Flutter SDK** >= 3.0.0
- **Python** 3.11+
- **Docker Desktop**
- **Git**

### 1. 启动Docker服务（开发后）

```bash
docker-compose up -d
```

### 2. 后端设置（开发后）

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. 前端设置

```bash
flutter pub get
flutter run
```

## 开发状态

当前版本：**MVP v1.0** (开发中)

- 🚧 Story 1.1: 项目初始化与用户注册（进行中）

## 参与贡献

欢迎贡献代码！详细开发指南将在项目搭建完成后更新。

---

**Built with ❤️ using Flutter, FastAPI, and AI**
