---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
  - '_bmad-output/planning-artifacts/research/market-ai-companion-apps-research-2026-01-07.md'
  - '_bmad-output/analysis/brainstorming-session-2026-01-07.md'
workflowType: 'architecture'
lastStep: 4
project_name: 'idol_private'
user_name: '李冬'
date: '2026-01-08'
prdCount: 1
uxDesignCount: 1
researchCount: 1
brainstormingCount: 1
---

# Architecture Decision Document - idol_private

**Author:** 李冬
**Date:** 2026-01-08

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

---

## 项目上下文分析（Project Context Analysis）

### 需求概览（Requirements Overview）

**功能需求分析（Functional Requirements）：**

idol_private包含**144个功能需求**，覆盖**18个能力领域**。这些需求定义了一个复杂的AI情感陪伴应用，核心能力包括：

**核心功能域及其架构影响：**

1. **AI对话与情感交互（FR11-FR24）**
   - 需要支持"人情味"对话风格：口语化、情绪词、犹豫感、不完美表达
   - 偶像可以识别用户情绪、提供情感共鸣、自然引用过去记忆
   - **架构影响**：需要定制化AI引擎（Qwen 7B fine-tuning或高级prompt engineering），记忆检索与上下文注入机制

2. **偶像生活系统（FR25-FR31）**
   - 时间驱动的有限状态机（FSM）：偶像根据时间段拥有不同状态（练歌、看书、休息、想你）
   - 生活事件在时间线上保持逻辑一致性，可被用户查询和在对话中提及
   - **架构影响**：需要FSM引擎、事件调度器、状态持久化、逻辑一致性验证机制

3. **记忆与个性化（FR32-FR38）**
   - 三层记忆系统：
     - 短期记忆（当前会话上下文）
     - 长期记忆（用户偏好、重要事件、情感模式）
     - 情感模式识别（追踪用户情绪变化和触发点）
   - **架构影响**：需要混合存储策略（Redis短期 + ChromaDB向量长期 + PostgreSQL结构化）、记忆检索算法、情感分析引擎

4. **用户关系发展（FR39-FR45）**
   - 亲密度养成系统（Lv1-100）：基于对话次数、时长、情感深度自动提升
   - 不同等级解锁不同对话深度，免费用户上限Lv20
   - **架构影响**：需要亲密度计算引擎、进度追踪、内容分级控制、防刷机制

5. **订阅与支付管理（FR46-FR53）**
   - Freemium模型：免费10条消息/天 + Lv20上限，付费版无限制
   - 应用内支付（iOS App Store / Android Google Play）
   - **架构影响**：需要精确消息计量、订阅状态同步（App Store/Google Play API）、功能访问控制

6. **通知与提醒（FR54-FR61）**
   - 每日早安/晚安推送（时间窗口：7-9点 / 21-23点）
   - 流失唤回（连续3天未登录）、个性化内容（包含昵称、最近对话引用）
   - **架构影响**：需要定时任务调度、时区感知、推送服务集成（FCM/APNs）、个性化内容生成

7. **运营与内容管理（FR62-FR72）**
   - 用户行为分析（留存率、日活、使用时长、"懂我"关键词触发率）
   - AI对话质量监控（异常报告、"太像机器人"标记、情绪求助场景高亮）
   - **架构影响**：需要分析管道、实时指标计算、运营后台、数据可视化

8. **客服与审核（FR73-FR86）**
   - 客服人员可查看用户对话、记忆数据、账户信息，支持搜索和诊断
   - 手动编辑记忆、发送补偿、处理举报
   - **架构影响**：需要权限控制系统、审计日志、客服工具界面、数据访问API

9. **数据与隐私管理（FR87-FR94）**
   - 用户可导出、删除所有数据；30天注销缓冲期
   - 所有数据加密传输（HTTPS）和存储（对话、用户信息）
   - **架构影响**：需要数据导出工具、删除工作流、加密密钥管理、安全审计日志

10. **平台与设备支持（FR95-FR102）**
    - 跨平台支持：Android 6.0+、iOS 12.0+、Web浏览器
    - 响应式布局（4.5"-7"屏幕）、深色模式、无网络友好提示
    - **架构影响**：Flutter前端、响应式UI框架、网络状态检测与重连机制

11. **内容审核与安全（FR103-FR109）**
    - 敏感词过滤（性、暴力、政治、歧视）、情绪求助场景自动高亮
    - 用户举报、24小时人工review、严重违规立即下架
    - **架构影响**：需要内容审核引擎、敏感词库、举报工作流、审核队列

12. **增强能力（FR110-FR138）**
    - 功能引导、里程碑庆祝、帮助中心、多设备登录与同步
    - 获客渠道追踪、实时监控（AI成本、响应时间、性能）
    - AI引擎切换（Ollama/Deepseek/Claude）、A/B测试支持
    - **架构影响**：需要配置管理系统、多设备同步机制、监控告警、渠道归因、实验平台

**功能规模评估：**
- **MVP范围**：约100个核心FR（FR1-FR61 + FR87-FR102 + FR110-FR138）
- **运营/客服工具**：约40个FR（FR62-FR86 + FR115-FR129）
- **Phase 2占位**：6个FR（FR139-FR144，语音、社交、多语言）

---

**非功能需求分析（Non-Functional Requirements）：**

idol_private定义了**6大类非功能需求**，这些质量属性直接驱动架构决策：

**1. 性能要求（Performance）- 直接影响用户"真实感"体验**

| NFR | 指标 | 目标值 | 架构影响 |
|-----|------|--------|---------|
| **NFR-P1** | AI对话响应时间 | 平均 < 2秒，95分位 < 5秒 | AI引擎选型、缓存策略、异步处理 |
| **NFR-P2** | App启动时间 | Android < 3秒，iOS < 2.5秒 | 资源懒加载、代码分割、启动优化 |
| **NFR-P3** | 对话历史加载 | 首次/滚动加载 < 1秒 | 数据库索引优化、分页策略 |
| **NFR-P4** | 内存占用 | 正常 < 200MB，峰值 < 300MB | 内存管理、对话历史缓存限制 |
| **NFR-P5** | 电池消耗 | 后台 < 1%/小时，活跃 < 5%/小时 | 后台任务优化、网络请求合并 |
| **NFR-P6** | App包大小 | Android < 50MB，iOS < 40MB | 资源压缩、代码混淆、按需下载 |
| **NFR-P7** | 并发处理能力 | MVP 50并发 → Growth 500并发 → Expansion 2000并发 | 水平扩展架构、负载均衡、无状态服务 |

**关键洞察**：NFR-P1（AI响应 < 2秒）是最严格约束 - 如果用户等待时间过长，会破坏"真实对话"的情感沉浸感。这直接影响AI引擎选型（Ollama本地 vs Deepseek API权衡）和缓存策略（常见问题预生成回复）。

**2. 安全要求（Security）- 用户深度个人信息保护**

| NFR | 要求 | 架构影响 |
|-----|------|---------|
| **NFR-S1** | 数据传输加密（HTTPS TLS 1.2+） | API Gateway SSL配置、证书管理 |
| **NFR-S2** | 数据存储加密（对话、用户信息、记忆） | 数据库加密、密钥管理服务 |
| **NFR-S3** | 用户认证（JWT，≤7天过期） | Token管理、安全存储（Keychain/KeyStore） |
| **NFR-S4** | 访问控制（多租户隔离、权限审计） | 权限系统、行级安全、审计日志 |
| **NFR-S5** | 隐私合规（中国个人信息保护法、GDPR） | 数据删除工作流、导出工具、隐私政策 |
| **NFR-S6** | 支付安全（不存储支付信息） | App Store/Google Play API集成 |
| **NFR-S7** | 代码混淆和防逆向 | ProGuard/Obfuscation、API密钥服务器端 |

**关键洞察**：用户会在对话中分享深度个人信息（情感、隐私、生活细节），数据泄露会完全摧毁信任。多租户隔离（NFR-S4）和端到端加密（NFR-S1/S2）是架构基础要求。

**3. 扩展性要求（Scalability）- 从MVP到5000付费用户的平滑增长**

| NFR | 扩展路径 | 架构影响 |
|-----|---------|---------|
| **NFR-SC1** | 用户规模扩展（10倍增长，性能下降 < 10%） | 无状态服务、数据库分片、缓存层 |
| **NFR-SC2** | 基础设施扩展路径 | 单VPS → 负载均衡 → GPU云 → 云端AI服务 |
| **NFR-SC3** | 数据增长支持（3年对话历史） | 数据归档策略、冷热数据分离 |

**扩展路径明细：**
- **0-100用户**：单台VPS + Ollama本地（10-50并发，¥500/月）
- **100-500用户**：2-3台VPS + 负载均衡（50-150并发，¥1500-2000/月）
- **500-2000用户**：切换Deepseek API 或 GPU云（500并发，¥5000/月）
- **2000-5000用户**：云端AI服务 + 缓存优化（2000并发，¥10000/月）

**关键洞察**：架构必须支持**AI引擎可切换**（Ollama → Deepseek/Claude），不能硬编码。需要抽象AI Provider接口，支持运行时切换（FR121）。

**4. 可维护性要求（Maintainability）**

| NFR | 要求 | 架构影响 |
|-----|------|---------|
| **NFR-M1** | AI引擎可切换（Ollama/Deepseek/Claude） | Provider抽象层、配置驱动 |
| **NFR-M2** | 偶像人格可扩展（MVP 1个 → Future多个） | 人格配置化、FSM模板化 |
| **NFR-M3** | 代码可读性（团队协作、AI Agent实现） | 清晰架构边界、文档化API |

**5. 可观测性要求（Observability）**

| NFR | 监控指标 | 架构影响 |
|-----|---------|---------|
| **NFR-O1** | 实时性能监控（AI响应时间、错误率、内存） | 监控告警系统、日志聚合 |
| **NFR-O2** | AI推理成本追踪（每用户成本、总成本） | 成本计量、预算告警 |
| **NFR-O3** | 对话质量评分（自动质量评分、记忆召回率） | 质量评估管道、指标存储 |
| **NFR-O4** | 用户行为分析（留存、使用时长、关键词触发率） | 分析管道、实时仪表板 |

**6. 合规性要求（Compliance）**

| NFR | 要求 | 架构影响 |
|-----|------|---------|
| **NFR-C1** | 应用商店合规（iOS App Store、Google Play） | 内容审核、年龄限制、隐私政策 |
| **NFR-C2** | 中国法律法规合规（个人信息保护法） | 数据本地化、用户同意机制 |
| **NFR-C3** | 内容安全（敏感词过滤、情绪求助高亮） | 内容审核引擎、人工review工作流 |

---

**规模与复杂度评估（Scale & Complexity）：**

**项目复杂度：High**

虽然是MVP阶段项目，但技术复杂度显著高于标准移动应用：

**复杂度指标分析：**

| 指标 | 评估 | 理由 |
|-----|------|------|
| **实时特性需求** | ✅ 高 | AI对话 < 2秒、状态变化实时同步、推送通知 |
| **多租户需求** | ✅ 中 | 每用户完全隔离的对话、记忆、订阅数据 |
| **监管合规需求** | ✅ 中 | 内容审核、隐私合规、应用商店政策 |
| **集成复杂度** | ✅ 高 | AI引擎、向量数据库、支付平台、推送服务 |
| **用户交互复杂度** | ✅ 高 | Material Design 3、响应式UI、无障碍访问 |
| **数据复杂度** | ✅ 高 | 三层记忆系统、FSM状态管理、向量检索 |

**技术域分类：**
- **Primary domain**: Full-Stack Mobile-First AI Application
- **Secondary domains**:
  - AI/ML Engineering（对话引擎、情感分析、质量评分）
  - 实时系统（WebSocket、状态同步、推送）
  - 数据工程（向量检索、分析管道、指标计算）
  - DevOps（监控、告警、成本优化）

**预估架构组件数量：18个核心组件**

**前端层（4个组件）：**
1. 对话界面模块（AI对话、历史记录、打字指示器）
2. 偶像状态展示模块（FSM可视化、时间线、状态卡片）
3. 亲密度系统模块（进度追踪、等级庆祝、里程碑）
4. 订阅管理模块（Freemium边界、支付、账户管理）

**后端服务层（7个服务）：**
1. **API Gateway**（路由、认证、限流）
2. **对话引擎服务**（AI Provider抽象、记忆注入、上下文管理）
3. **FSM引擎服务**（状态调度、事件队列、逻辑验证）
4. **记忆管理服务**（短期/长期记忆、向量检索、情感模式识别）
5. **用户管理服务**（认证、授权、订阅状态、设备同步）
6. **分析服务**（实时指标、用户行为、AI质量监控）
7. **运营后台服务**（客服工具、内容管理、配置管理）

**数据层（4个存储系统）：**
1. **PostgreSQL**（用户账户、对话历史、订阅记录、FSM状态）
2. **Redis**（短期会话记忆、亲密度缓存、消息队列）
3. **ChromaDB**（长期向量记忆、语义检索）
4. **对象存储**（用户头像、数据导出文件、日志归档）

**基础设施层（3个支撑系统）：**
1. **AI推理服务**（Ollama/Deepseek/Claude抽象层）
2. **通知服务**（FCM/APNs集成、定时调度、个性化）
3. **监控告警系统**（性能监控、成本追踪、质量评分）

---

### 技术约束与依赖（Technical Constraints & Dependencies）

**已知技术栈（来自PRD明确定义）：**

**前端技术栈：**
- **框架**：Flutter（单一代码库，覆盖Android + iOS + Web）
- **UI系统**：Material Design 3 + Custom Theme（温暖陪伴型设计）
- **状态管理**：_待架构决策_（候选：Provider / Riverpod / Bloc）
- **最低支持版本**：Android 6.0+ (API 23+) / iOS 12.0+

**后端技术栈：**
- **API框架**：FastAPI（Python，异步支持）
- **AI引擎**：
  - **主方案**：Ollama + Qwen 7B本地部署（成本优化）
  - **备选方案**：Deepseek API / Claude API（质量保障，¥5000-10000/月预算）
- **数据库**：
  - **关系数据库**：PostgreSQL（用户、对话、订阅、FSM状态）
  - **缓存**：Redis（会话记忆、消息队列、亲密度缓存）
  - **向量数据库**：ChromaDB（长期记忆、语义检索）

**关键技术约束：**

**1. 成本约束（最严格）：**
- **每用户AI推理成本 < ¥2/月**（确保60%利润率）
- **基础设施成本路径**：
  - MVP（0-100用户）：¥500/月（单VPS）
  - Growth（100-500用户）：¥1500-2000/月（2-3台VPS）
  - Expansion（500-5000用户）：¥5000-10000/月（API或GPU云）
- **架构影响**：优先Ollama本地部署，但架构必须支持切换到API（不能硬编码）

**2. AI引擎可切换约束：**
- FR121明确要求：运营人员可配置AI后端（Ollama/Deepseek/Claude）
- **架构影响**：需要AI Provider抽象层，支持运行时切换，配置驱动

**3. 性能约束：**
- AI响应 < 2秒（平均）- 直接影响用户"真实感"
- App冷启动 < 3秒（Android）- 影响首次体验
- **架构影响**：需要缓存策略、异步处理、资源优化

**4. 安全约束：**
- 所有数据传输加密（HTTPS TLS 1.2+）
- 所有敏感数据存储加密（对话、用户信息、记忆）
- **架构影响**：密钥管理服务、端到端加密、审计日志

**5. 合规约束：**
- 内容审核（敏感词过滤）- 应用商店要求
- 中国个人信息保护法合规（数据删除、导出、隐私政策）
- **架构影响**：内容审核引擎、数据管理工作流

**技术依赖清单：**

**核心依赖（MVP必需）：**
- Flutter SDK（前端框架）
- FastAPI（后端API）
- PostgreSQL（关系数据库）
- Redis（缓存和队列）
- ChromaDB（向量数据库）
- Ollama + Qwen 7B（AI引擎主方案）
- iOS App Store / Google Play（支付和分发）
- FCM / APNs（推送通知）

**备选依赖（Plan B）：**
- Deepseek API（如Ollama质量不达标）
- Claude API（如需更高质量对话）
- GPU云服务（如需更高并发）

**开发工具依赖：**
- Git（版本控制）
- Docker（本地开发环境）
- GitHub Actions 或 GitLab CI（CI/CD）
- Sentry 或 类似（错误追踪）
- Grafana + Prometheus（监控告警）

---

### 跨领域关注点（Cross-Cutting Concerns）

以下关注点影响多个架构组件，需要在架构设计中统一解决：

**1. 数据一致性（Data Consistency）**

**挑战：**
- 用户记忆、对话历史、亲密度必须强一致（不能丢失或矛盾）
- 多个数据库（PostgreSQL、Redis、ChromaDB）之间的同步
- FR131要求跨设备同步对话、亲密度、订阅状态

**架构影响：**
- 需要事务管理策略（数据库事务 vs 分布式事务）
- 数据同步机制（实时同步 vs 最终一致性）
- 冲突解决策略（多设备同时操作时的处理）

---

**2. 实时性要求（Real-Time Requirements）**

**挑战：**
- AI响应延迟 < 2秒（NFR-P1）
- 偶像状态变化需要实时展示
- 打字指示器（用户正在输入 / 偶像正在回复）
- 推送通知低延迟（早安/晚安、流失唤回）

**架构影响：**
- 需要WebSocket或Server-Sent Events（双向实时通信）
- 异步消息队列（解耦AI推理和用户界面）
- 缓存策略（减少数据库查询延迟）

---

**3. 可观测性（Observability）**

**挑战：**
- FR115-FR118要求实时监控：AI响应时间、错误率、成本、性能
- FR126要求AI回复自动质量评分
- FR127要求记忆召回准确率指标
- 需要追踪用户行为（留存、使用时长、关键词触发率）

**架构影响：**
- 需要统一日志聚合（结构化日志、分布式追踪）
- 实时指标计算管道
- 监控告警系统（性能异常、成本超标）
- 数据可视化仪表板（运营后台）

---

**4. 多租户隔离（Multi-Tenancy Isolation）**

**挑战：**
- 每个用户的对话、记忆、订阅完全隔离（NFR-S4）
- 客服和运营人员访问需要权限控制和审计日志
- 防止数据泄露和越权访问

**架构影响：**
- 数据库行级安全（Row-Level Security）
- API层权限验证（每个请求校验用户身份）
- 审计日志（记录所有数据访问）

---

**5. AI引擎抽象与可切换性（AI Provider Abstraction）**

**挑战：**
- FR121要求运营人员可切换AI后端（Ollama/Deepseek/Claude）
- 不同AI引擎有不同API、定价、响应格式
- 需要在不修改业务逻辑的情况下切换AI引擎

**架构影响：**
- 需要AI Provider抽象层（统一接口）
- 配置驱动的AI引擎选择（运行时切换）
- 适配器模式（Adapter Pattern）封装不同AI API

---

**6. 内容安全与审核（Content Safety & Moderation）**

**挑战：**
- FR103-FR109要求敏感词过滤、情绪求助高亮、用户举报处理
- 应用商店合规要求（内容审核、年龄限制）
- 需要平衡自动化审核和人工review

**架构影响：**
- 内容审核引擎（敏感词库、规则引擎）
- 审核队列（举报工单、待review对话）
- 人工review工作流（24小时内处理举报）

---

**7. 成本优化与监控（Cost Optimization & Monitoring）**

**挑战：**
- 每用户AI推理成本必须 < ¥2/月（NFR-P7）
- FR118要求实时AI推理成本数据
- 需要在成本和质量之间找到平衡点

**架构影响：**
- 成本计量（追踪每次AI调用的token消耗和费用）
- 缓存策略（常见问题预生成回复，减少AI调用）
- 预算告警（成本超标时自动告警）
- 智能路由（高峰期优化流量分配）

---

**8. 可扩展性与模块化（Scalability & Modularity）**

**挑战：**
- NFR-M2要求偶像人格可扩展（MVP 1个 → Future多个）
- 架构需要支持从50用户到5000用户的平滑扩展
- 不同功能模块需要独立扩展（AI推理、数据库、通知服务）

**架构影响：**
- 微服务架构 vs 模块化单体（需权衡）
- 人格配置化（FSM模板、对话风格参数化）
- 水平扩展设计（无状态服务、负载均衡）

---

这个项目上下文分析为接下来的架构决策提供了坚实基础，确保所有架构选择都基于实际需求和约束，而不是主观假设。

---

## 初始化模板评估（Starter Template Evaluation）

### 主要技术域识别（Primary Technology Domain）

基于项目需求分析，idol_private是一个**Full-Stack Mobile-First AI Application**，包含以下技术组件：

- **前端**: Flutter（跨平台：Android + iOS + Web）
- **后端**: FastAPI（Python异步API框架）
- **数据层**: PostgreSQL + Redis + ChromaDB
- **AI引擎**: Ollama + Qwen 7B

这不是传统的单一技术栈项目（如纯Web应用），而是**多组件架构（Multi-Component Architecture）**，需要协调前端、后端、AI服务和多个数据存储。

### 项目组织策略：Monorepo vs Multi-Repo

经过评估，我推荐使用**Monorepo结构**，原因如下：

**Monorepo优势（针对idol_private）：**
- Flutter前端和FastAPI后端紧密耦合（AI陪伴应用，共享数据模型、API契约）
- 简化跨组件更改（例如：新增亲密度系统，需要同时修改前端UI和后端计算逻辑）
- 统一版本控制和发布流程（MVP阶段快速迭代）
- 共享开发工具配置（linting、formatting、pre-commit hooks）

**参考来源**：根据[FastAPI社区讨论](https://github.com/fastapi/fastapi/discussions/4344)和[Flutter monorepo最佳实践](https://blog.codemagic.io/flutter-monorepos/)，对于紧密关联的前后端项目，monorepo是更清晰的选择。

### 选定的项目结构：Hybrid Monorepo

**推荐的目录结构：**

```
idol_private/
├── frontend/                    # Flutter应用
│   ├── lib/
│   │   ├── main.dart
│   │   ├── features/            # 按功能组织（conversation, idol_life, intimacy, subscription）
│   │   ├── core/                # 核心工具和配置
│   │   ├── shared/              # 共享组件和模型
│   │   └── config/
│   ├── test/
│   ├── pubspec.yaml
│   └── README.md
│
├── backend/                     # FastAPI应用
│   ├── app/
│   │   ├── main.py              # FastAPI入口
│   │   ├── api/
│   │   │   └── v1/              # API版本化
│   │   │       ├── routes/      # API路由（conversation, idol_life, user, subscription）
│   │   │       └── dependencies.py
│   │   ├── models/              # Pydantic模型和SQLAlchemy ORM
│   │   ├── schemas/             # API请求/响应Schema
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── conversation_engine.py
│   │   │   ├── fsm_engine.py
│   │   │   ├── memory_service.py
│   │   │   └── ai_provider/    # AI引擎抽象层
│   │   ├── core/                # 配置、安全、日志
│   │   ├── database/            # 数据库连接和会话管理
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md
│
├── docs/                        # 项目文档
│   ├── api/                     # API文档
│   ├── architecture/            # 架构决策记录
│   └── deployment/              # 部署指南
│
├── scripts/                     # 构建和部署脚本
│   ├── init-dev.sh              # 开发环境初始化
│   ├── build-flutter.sh
│   └── deploy.sh
│
├── .github/                     # CI/CD配置
│   └── workflows/
│
├── docker/                      # Docker配置（可选，用于本地开发环境）
│   ├── Dockerfile.backend
│   └── docker-compose.yml
│
├── .gitignore
├── README.md
└── LICENSE
```

**结构设计理念：**
- **前后端分离但共享一个仓库**：frontend/和backend/是独立的子项目，各自有自己的依赖和配置
- **模块化功能组织**：frontend按feature组织（conversation、idol_life、intimacy），backend按service组织（conversation_engine、fsm_engine、memory_service）
- **清晰的责任边界**：API契约通过OpenAPI Schema共享，但代码实现完全独立
- **MVP优先，易于扩展**：当前结构支持MVP快速开发，未来可以根据需要拆分为微服务

### 初始化命令（Initialization Commands）

**步骤1：初始化Flutter前端**

```bash
# 创建Flutter项目（指定组织ID和平台）
flutter create \
  --org com.idolprivate \
  --platforms android,ios,web \
  --project-name idol_app \
  frontend

# 进入frontend目录
cd frontend

# 添加核心依赖（Material Design 3、状态管理、HTTP客户端）
flutter pub add material \
  http \
  provider \
  shared_preferences \
  flutter_secure_storage

# 添加开发依赖
flutter pub add --dev flutter_test mockito build_runner
```

**关键选项说明**：
- `--org com.idolprivate`：设置组织ID（用于App Store和Google Play包名）
- `--platforms android,ios,web`：明确指定支持的平台
- `--project-name idol_app`：遵循lowercase_with_underscores命名约定

**参考来源**：[Flutter CLI官方文档](https://docs.flutter.dev/reference/flutter-cli)和[2026最佳实践](https://www.manektech.com/blog/flutter-development-best-practices)

**步骤2：初始化FastAPI后端**

```bash
# 创建backend目录结构
mkdir -p backend/app/{api/v1/routes,models,schemas,services,core,database,utils}
mkdir -p backend/tests

# 创建FastAPI入口文件
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="idol_private API",
    openapi_url="/api/v1/openapi.json"
)

# CORS配置（允许Flutter前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
EOF

# 创建requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.6.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.10
redis==5.2.0
chromadb==0.5.15
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
httpx==0.27.2
EOF
```

**结构设计理念**（参考[FastAPI生产级项目结构](https://medium.com/@devsumitg/the-perfect-structure-for-a-large-production-ready-fastapi-app-78c55271d15c)）：
- **Module-Functionality Structure**：按模块功能组织（conversation、idol_life、user、subscription）
- **Separation of Concerns**：routers（路由）、models（数据模型）、schemas（API Schema）、services（业务逻辑）严格分离
- **Environment-Driven Configuration**：使用Pydantic Settings管理配置（.env文件）
- **Dependency Injection**：FastAPI的依赖注入保证代码可测试性

### 架构决策记录（Architectural Decisions from Starter）

**语言与运行时（Language & Runtime）：**
- **前端**：Dart（Flutter SDK >= 3.0.0）
- **后端**：Python 3.11+（异步支持，FastAPI最佳性能）
- **类型系统**：Dart静态类型 + Python类型提示（Pydantic强制类型验证）

**样式解决方案（Styling Solution）：**
- **UI框架**：Material Design 3（Flutter内置支持）
- **主题系统**：温暖陪伴型设计（Custom Theme，基于UX规范）
- **响应式布局**：Flutter LayoutBuilder + MediaQuery（支持320px-1024px+）

**构建工具（Build Tooling）：**
- **前端**：Flutter Build System（支持Android APK/AAB、iOS IPA、Web）
- **后端**：Uvicorn（ASGI服务器）+ Gunicorn（生产环境进程管理）
- **代码质量**：
  - Dart: `flutter analyze`（静态分析）
  - Python: Ruff（linting + formatting）+ Black（代码格式化）+ MyPy（类型检查）

**测试框架（Testing Framework）：**
- **前端**：Flutter Test（单元测试）+ Integration Test（集成测试）
- **后端**：Pytest（单元测试 + API测试）+ pytest-asyncio（异步测试支持）
- **Mock/Stub**：Mockito（Flutter）+ unittest.mock（Python）

**代码组织（Code Organization）：**
- **前端**：Feature-First Architecture（按功能模块组织：conversation、idol_life、intimacy、subscription）
- **后端**：Layered Architecture（routers → services → models → database）
- **共享模型**：通过OpenAPI Schema共享API契约（后端生成 → 前端自动生成Dart客户端）

**开发体验（Development Experience）：**
- **Hot Reload**：Flutter Hot Reload（前端）+ Uvicorn --reload（后端）
- **API文档**：FastAPI自动生成Swagger UI（`/docs`）和ReDoc（`/redoc`）
- **调试工具**：Flutter DevTools（前端性能分析）+ Python Debugger（后端）
- **环境管理**：Flutter SDK Manager + Python venv（虚拟环境）

### 为什么不使用传统"Starter Template"？

与传统Web应用（Next.js、Create React App）不同，idol_private是多组件AI应用，**没有现成的"一键生成"模板**满足以下需求：
- Flutter + FastAPI的组合
- AI引擎抽象层（Ollama/Deepseek/Claude可切换）
- 三层记忆系统（Redis + ChromaDB + PostgreSQL）
- FSM偶像生活系统
- 跨设备同步和实时通信

因此，我们采用**手动组织 + 最佳实践**的方式：
1. 使用`flutter create`初始化标准Flutter项目
2. 使用FastAPI生产级结构模板（参考社区最佳实践）
3. 自定义服务层架构（conversation_engine、fsm_engine、memory_service）

**这种方式的优势**：
- **完全掌控架构决策**（不被starter template限制）
- **灵活扩展**（随时调整目录结构和模块划分）
- **MVP优先**（只创建当前需要的结构，避免过度工程）

### 初始化任务优先级

**第一个实现Story应该是：**
"**项目初始化和开发环境搭建（Project Initialization & Development Setup）**"

**Acceptance Criteria：**
- ✅ Monorepo目录结构创建完成
- ✅ Flutter前端项目初始化（`flutter create`）
- ✅ FastAPI后端项目结构创建（routers、models、schemas、services目录）
- ✅ 核心依赖安装完成（Flutter: http、provider; Python: fastapi、uvicorn、sqlalchemy）
- ✅ 开发环境脚本可用（`scripts/init-dev.sh`）
- ✅ Git仓库初始化（.gitignore配置正确）
- ✅ 后端健康检查端点可用（`GET /health` → `{"status": "healthy"}`）
- ✅ Flutter前端可以运行默认示例（`flutter run`）

**参考来源总结：**
- [Flutter CLI官方文档](https://docs.flutter.dev/reference/flutter-cli)
- [2026 Flutter最佳实践](https://www.manektech.com/blog/flutter-development-best-practices)
- [FastAPI生产级项目结构](https://medium.com/@devsumitg/the-perfect-structure-for-a-large-production-ready-fastapi-app-78c55271d15c)
- [FastAPI最佳实践（GitHub）](https://github.com/zhanymkanov/fastapi-best-practices)
- [Monorepo vs Multi-Repo讨论](https://github.com/fastapi/fastapi/discussions/4344)
- [Flutter Monorepo管理](https://blog.codemagic.io/flutter-monorepos/)

---

## 核心架构决策（Core Architectural Decisions）

### 决策优先级分析（Decision Priority Analysis）

**由PRD预先明确的技术栈（Pre-Determined by PRD）：**
- **数据库层**: PostgreSQL + Redis + ChromaDB（三层存储架构已固定）
- **前端框架**: Flutter（Android + iOS + Web跨平台）
- **后端框架**: FastAPI（Python异步API）
- **AI引擎**: Ollama + Qwen 7B（主方案），Deepseek/Claude API（备选）
- **认证机制**: JWT（≤7天过期，Keychain/KeyStore存储）
- **安全加密**: HTTPS TLS 1.2+，数据库加密存储

**由初始化模板决定（Determined by Starter Template - Step 3）：**
- **语言与运行时**: Dart（Flutter SDK >=3.0） + Python 3.11+
- **UI系统**: Material Design 3 + Custom Theme（温暖陪伴型设计）
- **构建工具**: Flutter Build System + Uvicorn/Gunicorn
- **测试框架**: Flutter Test + Pytest + pytest-asyncio
- **代码组织**: Feature-First（前端）+ Layered Architecture（后端）
- **项目结构**: Hybrid Monorepo（frontend/ + backend/）

**本步骤决策的关键架构选择（Critical Decisions Made in This Step）：**
1. ✅ **前端状态管理**: Riverpod 2.0+
2. ✅ **实时通信机制**: Server-Sent Events (SSE)
3. ✅ **AI Provider抽象**: Strategy + Factory Pattern
4. ✅ **缓存策略**: 三层缓存（对话上下文 + 常见问题 + 向量检索）
5. ✅ **部署基础设施**: VPS + Docker + Nginx（MVP），预留云迁移
6. ✅ **CI/CD管道**: GitHub Actions
7. ✅ **监控日志**: Grafana + Prometheus + Loki

**延后决策（Post-MVP，不阻塞实现）：**
- 语音功能（STT/TTS）- Phase 2功能占位
- 多语言支持 - Phase 2功能占位
- 社交分享功能 - Phase 2功能占位

---

### 前端架构决策（Frontend Architecture）

#### 1. 状态管理：Riverpod 2.0+

**决策理由：**

idol_private需要管理复杂的应用状态：
- **对话历史**：实时更新的消息列表、打字指示器
- **偶像FSM状态**：时间驱动的状态变化（早上练歌→下午看书→晚上想你）
- **亲密度系统**：Lv1-100的进度追踪、等级提升动画
- **订阅状态**：Freemium边界（免费10条/天，付费无限）
- **跨组件共享**：conversation、idol_life、intimacy模块需要共享数据

**选择Riverpod的原因：**
1. **编译时安全**：ProviderScope编译时检查，避免运行时错误（适合MVP快速迭代）
2. **测试友好**：Provider可以轻松mock，支持单元测试和集成测试
3. **性能优化**：自动依赖追踪，仅rebuild受影响的widget
4. **适合复杂状态**：支持StateNotifier、FutureProvider、StreamProvider组合使用
5. **官方推荐**：Riverpod是Provider的改进版，Flutter官方文档推荐用于大型应用

**实现示例：**
```dart
// lib/features/conversation/providers/conversation_provider.dart
final conversationProvider = StateNotifierProvider<ConversationNotifier, ConversationState>((ref) {
  return ConversationNotifier(ref.read(conversationRepositoryProvider));
});

class ConversationNotifier extends StateNotifier<ConversationState> {
  final ConversationRepository _repository;

  ConversationNotifier(this._repository) : super(ConversationState.initial());

  Future<void> sendMessage(String content) async {
    state = state.copyWith(isLoading: true);
    final response = await _repository.sendMessage(content);
    state = state.copyWith(
      messages: [...state.messages, response],
      isLoading: false,
    );
  }
}

// lib/features/idol_life/providers/idol_status_provider.dart
final idolStatusStreamProvider = StreamProvider<IdolStatus>((ref) {
  return ref.read(idolStatusRepositoryProvider).watchStatusChanges();
});
```

**版本**: `flutter_riverpod: ^2.6.1` (2026年1月最新稳定版)

---

#### 2. 实时通信：Server-Sent Events (SSE)

**决策理由：**

idol_private需要实时推送：
- **偶像状态变化**：FSM状态转换（练歌→看书→休息）
- **打字指示器**：偶像正在回复的实时反馈
- **可选：AI响应流式返回**（提升用户体验，看到AI"思考"过程）

**选择SSE的原因（相比WebSocket）：**
1. **单向通信足够**：偶像状态推送是服务器→客户端单向，SSE完美匹配
2. **实现简单**：FastAPI原生支持SSE，Flutter http库直接支持EventSource
3. **成本低**：SSE比WebSocket连接维护成本低（MVP阶段成本优先）
4. **HTTP协议**：无需额外端口，复用HTTPS连接，防火墙友好
5. **自动重连**：SSE自动处理断线重连

**渐进式升级路径**：
- **MVP**: 使用SSE推送偶像状态（每30秒）
- **Phase 2**: 如需双向实时（语音通话、多人聊天），切换到WebSocket

**FastAPI实现：**
```python
# backend/app/api/v1/routes/idol_status.py
from sse_starlette.sse import EventSourceResponse

@router.get("/idol/status/stream")
async def idol_status_stream(
    user_id: str = Depends(get_current_user_id)
):
    async def event_generator():
        while True:
            # 获取偶像当前状态
            status = await idol_fsm_service.get_current_status(user_id)

            # 推送状态更新
            yield {
                "event": "idol_status_update",
                "data": json.dumps({
                    "state": status.state,
                    "mood": status.mood,
                    "activity": status.activity,
                    "timestamp": status.timestamp.isoformat()
                })
            }

            # 等待30秒或状态变化
            await asyncio.sleep(30)

    return EventSourceResponse(event_generator())
```

**Flutter客户端：**
```dart
// lib/features/idol_life/repositories/idol_status_repository.dart
Stream<IdolStatus> watchStatusChanges() async* {
  final client = HttpClient();
  final request = await client.getUrl(Uri.parse('$baseUrl/api/v1/idol/status/stream'));
  request.headers.add('Authorization', 'Bearer $token');

  final response = await request.close();
  await for (var event in response.transform(utf8.decoder).transform(LineSplitter())) {
    if (event.startsWith('data:')) {
      final data = json.decode(event.substring(5));
      yield IdolStatus.fromJson(data);
    }
  }
}
```

**依赖**: `sse_starlette: ^2.2.0` (FastAPI), `http: ^1.2.2` (Flutter)

---

### 后端架构决策（Backend Architecture）

#### 3. AI Provider抽象层：Strategy Pattern + Factory Pattern

**决策理由：**

FR121明确要求：**运营人员可配置AI推理后端（切换Ollama/Deepseek/Claude）**

**核心挑战：**
- 不同AI引擎有不同API格式（Ollama HTTP API vs Deepseek REST API vs Claude SDK）
- 不同定价模型（Ollama免费本地 vs Deepseek按Token计费 vs Claude按Request计费）
- 需要在**不修改业务逻辑**的情况下切换AI引擎（配置驱动）

**设计方案：**

**抽象基类（Strategy Pattern）**：
```python
# backend/app/services/ai_provider/base.py
from abc import ABC, abstractmethod
from typing import List, Dict

class AIProvider(ABC):
    """AI Provider抽象基类"""

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        user_profile: Dict
    ) -> str:
        """生成AI回复"""
        pass

    @abstractmethod
    async def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算本次调用成本（人民币）"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """获取Provider名称（用于日志和监控）"""
        pass
```

**Ollama Provider实现**：
```python
# backend/app/services/ai_provider/ollama_provider.py
class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "qwen:7b"

    async def generate_response(self, prompt: str, context: List[Dict], user_profile: Dict) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "context": context,
                    "temperature": 0.8,
                }
            )
            return response.json()["response"]

    async def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return 0.0  # Ollama本地部署，无直接成本

    def get_provider_name(self) -> str:
        return "ollama_qwen7b"
```

**Deepseek Provider实现**：
```python
# backend/app/services/ai_provider/deepseek_provider.py
class DeepseekProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    async def generate_response(self, prompt: str, context: List[Dict], user_profile: Dict) -> str:
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        return response.choices[0].message.content

    async def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        # Deepseek定价：¥1/1M input tokens, ¥2/1M output tokens
        input_cost = (input_tokens / 1_000_000) * 1.0
        output_cost = (output_tokens / 1_000_000) * 2.0
        return input_cost + output_cost

    def get_provider_name(self) -> str:
        return "deepseek_chat"
```

**Factory工厂（配置驱动）**：
```python
# backend/app/services/ai_provider/factory.py
from app.core.config import settings

class AIProviderFactory:
    @staticmethod
    def create_provider() -> AIProvider:
        provider_type = settings.AI_PROVIDER  # 从.env文件读取

        if provider_type == "ollama":
            return OllamaProvider(base_url=settings.OLLAMA_BASE_URL)
        elif provider_type == "deepseek":
            return DeepseekProvider(api_key=settings.DEEPSEEK_API_KEY)
        elif provider_type == "claude":
            return ClaudeProvider(api_key=settings.CLAUDE_API_KEY)
        else:
            raise ValueError(f"Unknown AI provider: {provider_type}")
```

**使用示例（业务逻辑层）**：
```python
# backend/app/services/conversation_engine.py
class ConversationEngine:
    def __init__(self):
        self.ai_provider = AIProviderFactory.create_provider()

    async def generate_reply(self, user_message: str, user_id: str) -> str:
        # 获取对话上下文和记忆
        context = await self.memory_service.get_context(user_id)
        user_profile = await self.user_service.get_profile(user_id)

        # 生成AI回复（不感知具体Provider）
        reply = await self.ai_provider.generate_response(
            prompt=user_message,
            context=context,
            user_profile=user_profile
        )

        # 记录成本
        cost = await self.ai_provider.calculate_cost(input_tokens=100, output_tokens=50)
        await self.analytics_service.record_ai_cost(user_id, cost)

        return reply
```

**配置切换（.env文件）**：
```bash
# MVP阶段：Ollama本地
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Growth阶段：切换到Deepseek
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxx
```

**优势**：
- ✅ **运行时切换**：修改.env文件后重启服务即可切换AI引擎
- ✅ **统一接口**：业务逻辑代码无需修改
- ✅ **易于扩展**：新增AI引擎只需实现AIProvider接口
- ✅ **成本追踪**：每个Provider实现自己的calculate_cost()

---

#### 4. 缓存策略：三层缓存架构

**决策理由：**

idol_private面临两个严格约束：
- **NFR-P1**: AI对话响应时间 < 2秒（平均）
- **成本约束**: 每用户AI推理成本 < ¥2/月

**缓存层次设计：**

**L1缓存：对话上下文缓存（Redis）**

- **目的**：减少AI每次请求时的记忆检索成本
- **内容**：最近50条对话上下文（用户消息 + 偶像回复）
- **TTL**：15分钟（用户离开后15分钟清除）
- **键设计**：`conv_ctx:{user_id}`
- **收益**：避免每次AI调用都查询PostgreSQL和ChromaDB

```python
async def get_conversation_context(user_id: str) -> List[Dict]:
    cache_key = f"conv_ctx:{user_id}"

    # 尝试从Redis获取
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 未命中，从数据库加载
    context = await db.query(Conversation).filter(user_id=user_id).limit(50).all()

    # 写入缓存
    await redis.setex(cache_key, 900, json.dumps(context))
    return context
```

**L2缓存：常见问题预生成回复（Redis）**

- **目的**：降低AI调用频率（成本优化）
- **内容**：高频问题的预生成AI回复（"早上好"、"在吗"、"在做什么"）
- **TTL**：24小时
- **键设计**：`common_resp:{question_hash}`
- **收益**：避免重复调用AI生成相同问题的回复

```python
COMMON_QUESTIONS_CACHE = {
    "早上好": "早上好呀！今天天气不错，适合练歌~ 你吃早餐了吗？",
    "在吗": "在在在！刚刚在想你呢，怎么了？",
    "在做什么": "{dynamic_activity}",  # 根据FSM状态动态生成
}

async def check_common_question_cache(user_message: str) -> Optional[str]:
    # 计算问题哈希
    question_hash = hashlib.md5(user_message.encode()).hexdigest()
    cache_key = f"common_resp:{question_hash}"

    # 检查缓存
    cached_reply = await redis.get(cache_key)
    if cached_reply:
        ai_call_avoided_counter.inc()  # Prometheus指标
        return cached_reply

    return None
```

**L3缓存：向量记忆检索结果（Redis）**

- **目的**：减少ChromaDB向量检索延迟
- **内容**：ChromaDB语义检索结果（用户相关记忆）
- **TTL**：10分钟
- **键设计**：`vec_search:{user_id}:{query_hash}`
- **收益**：避免重复的向量数据库查询

```python
async def search_user_memory(user_id: str, query: str) -> List[Memory]:
    query_hash = hashlib.md5(query.encode()).hexdigest()
    cache_key = f"vec_search:{user_id}:{query_hash}"

    # 尝试缓存
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 未命中，查询ChromaDB
    results = chromadb_client.query(
        collection_name=f"user_{user_id}_memory",
        query_texts=[query],
        n_results=5
    )

    # 写入缓存
    await redis.setex(cache_key, 600, json.dumps(results))
    return results
```

**缓存失效策略：**
- **主动失效**：用户发送新消息时，清除L1对话上下文缓存
- **被动失效**：TTL自动过期
- **全局失效**：AI引擎切换时，清除所有L2常见问题缓存

**预期效果：**
- **响应时间**：缓存命中率60%+，平均响应时间从3秒降至1.5秒
- **成本节省**：避免30%的AI调用，每用户成本从¥2.5降至¥1.8

---

### 基础设施与部署决策（Infrastructure & Deployment）

#### 5. 部署架构：VPS + Docker + Nginx（MVP），预留云迁移路径

**决策理由：**

idol_private的成本约束非常严格：
- **MVP阶段（0-100用户）**：¥500/月
- **Growth阶段（100-500用户）**：¥1500-2000/月
- **Expansion阶段（500-5000用户）**：¥5000-10000/月

云服务（AWS/Aliyun）在MVP阶段成本过高，选择VPS + Docker自建。

**MVP阶段架构（0-100用户）：**

**VPS选择**：
- **提供商**: DigitalOcean / Vultr / Hetzner
- **配置**: 8核16GB，200GB SSD，5TB流量
- **成本**: ¥500/月（约$70）
- **地域**: 中国香港/新加坡（低延迟）

**技术栈**：
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx（负载均衡、SSL终止、静态文件服务）
- **AI推理**: Ollama容器（CPU推理，GPU可选）
- **数据库**: PostgreSQL + Redis容器
- **SSL证书**: Let's Encrypt（免费）

**Docker Compose配置**：
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/idol_db
      - REDIS_URL=redis://redis:6379
      - AI_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - ./backend:/app

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=idol_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

  ollama:
    image: ollama/ollama:latest
    restart: always
    volumes:
      - ollama_models:/root/.ollama
    # GPU支持（可选）
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  ollama_models:
```

**Nginx配置（SSL + 反向代理）**：
```nginx
upstream backend_api {
    server backend:8000;
}

server {
    listen 80;
    server_name api.idolprivate.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.idolprivate.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    location /api/ {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://backend_api/docs;
    }
}
```

**Growth阶段扩展（100-500用户）：**
- 增加2台VPS，Nginx负载均衡（Round Robin）
- PostgreSQL主从复制（异步复制）
- Redis Sentinel高可用（3节点）

**Expansion阶段迁移（500-5000用户）：**
- 切换到云服务（Aliyun / Tencent Cloud）
- 切换AI引擎到Deepseek/Claude API（本地GPU成本过高）
- 使用托管数据库（RDS PostgreSQL + ElastiCache Redis）
- CDN加速（Cloudflare / Aliyun CDN）

---

#### 6. CI/CD管道：GitHub Actions

**决策理由：**
- **免费额度**：GitHub Actions提供2000分钟/月免费额度（MVP足够）
- **集成度高**：与GitHub深度集成，无需额外配置
- **生态丰富**：大量官方和社区Action可用

**Pipeline设计**：

**Backend CI Pipeline**：
```yaml
name: Backend CI
on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint with Ruff
        run: |
          cd backend
          ruff check .

      - name: Type check with MyPy
        run: |
          cd backend
          mypy app/

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Frontend CI Pipeline**：
```yaml
name: Frontend CI
on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.0'

      - name: Install dependencies
        run: |
          cd frontend
          flutter pub get

      - name: Analyze code
        run: |
          cd frontend
          flutter analyze

      - name: Run tests
        run: |
          cd frontend
          flutter test
```

**CD Pipeline（自动部署到VPS）**：
```yaml
name: Deploy to VPS
on:
  push:
    branches: [main]

jobs:
  deploy:
    needs: [backend-test, frontend-test]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /app/idol_private
            git pull origin main
            docker-compose down
            docker-compose up -d --build
            docker-compose logs --tail=50
```

---

#### 7. 监控与日志：Grafana + Prometheus + Loki

**决策理由：**

FR115-FR118明确要求：
- **实时性能监控**：AI响应时间、错误率、内存占用
- **AI成本追踪**：每用户成本、总成本
- **质量监控**：AI回复质量评分、记忆召回准确率

**监控栈选择：**
- **Prometheus**: 时序数据库，收集指标
- **Grafana**: 可视化仪表板
- **Loki**: 日志聚合（轻量级ELK替代）
- **成本**: 全部开源免费

**监控指标设计：**

**性能指标（Prometheus）**：
```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# AI响应时间
ai_response_time = Histogram(
    'ai_response_seconds',
    'AI response time in seconds',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0]
)

# AI Token消耗
ai_tokens_consumed = Counter(
    'ai_tokens_total',
    'Total AI tokens consumed',
    ['user_id', 'provider']
)

# AI成本
ai_cost_per_user = Gauge(
    'ai_cost_per_user_yuan',
    'AI cost per user in CNY',
    ['user_id']
)

# 记忆召回准确率
memory_recall_accuracy = Gauge(
    'memory_recall_accuracy',
    'Memory recall accuracy percentage'
)

# API错误率
api_error_rate = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'status_code']
)
```

**使用示例**：
```python
# 记录AI响应时间
with ai_response_time.time():
    response = await ai_provider.generate_response(prompt, context)

# 记录Token消耗和成本
ai_tokens_consumed.labels(user_id=user.id, provider="ollama").inc(response.tokens)
cost = await ai_provider.calculate_cost(input_tokens, output_tokens)
ai_cost_per_user.labels(user_id=user.id).set(cost)
```

**Grafana仪表板设计**：

**Dashboard 1: AI性能监控**
- AI平均响应时间（P50/P95/P99）
- AI调用量趋势（每小时/每天）
- AI错误率（按Provider分组）
- Token消耗趋势

**Dashboard 2: 成本监控**
- 每用户平均AI成本（Top 10用户）
- 总AI成本趋势（日/周/月）
- 成本预算告警（超过¥10000/月时告警）

**Dashboard 3: 用户行为监控**
- DAU/MAU
- 7日留存率
- 平均对话次数
- 亲密度分布

**Dashboard 4: 系统健康监控**
- API延迟（P50/P95/P99）
- 数据库连接池使用率
- Redis内存使用率
- 容器CPU/内存使用

**日志聚合（Loki）**：
```python
# backend/app/core/logging.py
import logging
import json

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_ai_request(self, user_id: str, provider: str, prompt: str, response_time: float):
        self.logger.info(json.dumps({
            "event": "ai_request",
            "user_id": user_id,
            "provider": provider,
            "prompt_length": len(prompt),
            "response_time": response_time
        }))
```

**部署配置（Docker Compose）**：
```yaml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
```

---

### 决策影响分析（Decision Impact Analysis）

**实施顺序（按依赖关系排序）：**

1. **项目初始化**（Story 1）
   - 执行Flutter create和FastAPI项目结构搭建
   - 安装核心依赖（Riverpod、http、fastapi、uvicorn）

2. **基础设施搭建**（Story 2-3）
   - 配置Docker Compose（PostgreSQL + Redis + Ollama）
   - 配置Nginx反向代理和SSL证书
   - 配置Prometheus + Grafana监控

3. **AI Provider抽象层**（Story 4）
   - 实现AIProvider基类和OllamaProvider
   - 实现Factory工厂和配置加载
   - 单元测试AI Provider切换逻辑

4. **缓存层实现**（Story 5）
   - 实现L1对话上下文缓存
   - 实现L2常见问题缓存
   - 实现L3向量检索缓存

5. **前端状态管理**（Story 6）
   - 配置Riverpod Providers（conversation、idol_status、intimacy、subscription）
   - 实现状态持久化和跨组件共享

6. **实时通信**（Story 7）
   - 实现FastAPI SSE端点（偶像状态流）
   - 实现Flutter SSE客户端（自动重连）

7. **CI/CD Pipeline**（Story 8）
   - 配置GitHub Actions（Backend CI + Frontend CI + CD）
   - 配置自动部署到VPS

**跨组件依赖：**

- **AI Provider ← 缓存层**：缓存层需要调用AI Provider的calculate_cost()
- **对话引擎 ← AI Provider + 缓存层**：对话引擎依赖AI Provider和缓存
- **前端状态管理 ← 实时通信**：Riverpod StreamProvider监听SSE流
- **监控 ← AI Provider + 缓存层**：Prometheus指标由AI Provider和缓存层提供

**风险缓解：**

- **Ollama质量不达标** → 2周内切换到Deepseek（已有抽象层，只需修改.env）
- **VPS性能不足** → 增加VPS或迁移到云（Docker配置可移植）
- **缓存命中率低** → 调整TTL和缓存策略（配置驱动）

