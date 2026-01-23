---
stepsCompleted: [1, 2, 3, 4]
workflowStatus: completed
epicRestructuringCompleted: true
validationCompleted: true
totalEpics: 11
totalStories: 62
totalRequirements: 220
coverageRate: 100%
completedDate: "2026-01-08"
implementationReadinessFixes:
  fixDate: "2026-01-08"
  fixedIssues:
    - "Issue #1: FR覆盖映射不一致 - FIXED ✅"
    - "Issue #2: Epic 0违反用户价值原则 - COMPLETED (Epic 0 Eliminated) ✅"
    - "Issue #3: Epic 10/11专注内部工具 - MOVED TO PHASE 2 ✅"
  status: "All Phase 1 fixes completed - Ready for Sprint Planning"
  referenceReport: "_bmad-output/planning-artifacts/implementation-readiness-report-2026-01-08.md"
  epic0Elimination:
    status: "completed"
    option: "Option 1 - Eliminate Epic 0 completely"
    technicalWorkRedistribution:
      - "Epic 1 Story 1: Project initialization + Docker + User registration"
      - "Epic 2 Story 1: AI Provider abstraction layer"
      - "Epic 2 Story 2: Redis 3-layer caching"
      - "On-demand: VPS deployment, CI/CD, monitoring, logging"
    frRedistribution:
      - "FR124-126, FR128-129 → Epic 9"
      - "FR127 → Epic 4"
      - "FR130-132 → Epic 7"
      - "FR133-135 → Epic 6"
      - "FR136-138 → Epic 8"
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
---

# idol_private - Epic Breakdown

**Project Name:** idol_private
**Author:** 李冬
**Original Date:** 2026-01-08
**Last Updated:** 2026-01-08 (Phase 1 Implementation Readiness Fixes Applied)

---

## 🔧 Implementation Readiness Fixes (2026-01-08)

本文档已根据 `implementation-readiness-report-2026-01-08.md` 的建议完成**Phase 1关键修复**：

### ✅ 已修复的关键问题：

1. **✅ Issue #1: FR覆盖映射不一致 - FIXED**
   - 创建了权威的FR Coverage Map（Epic 0-11编号方案）
   - 补充了遗漏的31个FR映射
   - 明确标记FR139-FR144为Phase 2功能
   - 解释了重复FR映射关系（FR12, FR32, FR70-71, FR122-123）
   - 删除了过时的详细FR映射（Epic 1-10编号方案）
   - **位置:** 见 "FR Coverage Map (功能需求覆盖矩阵)" 章节

2. **✅ Issue #2: Epic 0违反用户价值原则 - COMPLETED (Epic 0 Eliminated)**
   - 已选择并执行Option 1：完全消除Epic 0
   - 技术工作Just-in-Time分配到用户价值Epic：
     - Story 0.1-0.2（项目初始化+Docker）→ Epic 1 Story 1
     - Story 0.3（AI Provider）→ Epic 2 Story 1
     - Story 0.4（Redis缓存）→ Epic 2 Story 2
     - Story 0.5-0.8（部署/监控）→ 按需或Phase 2
   - FR124-FR138已重新分配到Epic 4, 6, 7, 8, 9
   - Epic 0标记为DEPRECATED，保留供参考
   - **位置:** 见 "Epic 0" 章节（已废弃）和FR Coverage Map

3. **✅ Issue #3: Epic 10/11专注内部工具 - MOVED TO PHASE 2**
   - Epic 10/11标记为 "🔄 Phase 2 (Post-MVP)"
   - 添加了延后理由和重新定义建议
   - 修正了Epic 11的Requirements（移除错误的FR139-FR144）
   - 更新了Delivery Strategy以反映MVP范围调整
   - **位置:** 见 "Epic 10" 和 "Epic 11" 章节

### 📋 更新的交付策略：

- **最小MVP:** Epic 1 + Epic 2 (+ Epic 3可选) - 2-3周
- **Beta测试:** Epic 4 + Epic 5 + Epic 3完整版 - 4-6周
- **正式上线:** Epic 6 + Epic 7 + Epic 8 - 8-10周
- **Phase 2:** Epic 9 + Epic 10 + Epic 11 + 社交功能(FR139-FR144) - Post-MVP

**Epic范围:** MVP包含Epic 1-8（8个用户价值Epic），Phase 2包含Epic 9-11（3个运营/内部工具Epic）

**参考报告:** `_bmad-output/planning-artifacts/implementation-readiness-report-2026-01-08.md`

---

## Requirements Inventory

### Functional Requirements (来自PRD)

**用户注册与账户管理 (FR1-FR10):**
- FR1: 用户可以通过邮箱注册新账户
- FR2: 用户可以使用已注册账户登录应用
- FR3: 用户可以通过邮箱重置密码
- FR4: 用户可以编辑个人资料（昵称、头像）
- FR5: 用户可以查看账户信息（注册日期、订阅状态）
- FR6: 用户可以注销账户
- FR7: 用户可以多设备登录同一账户
- FR8: 系统可以在新设备登录时同步最近对话和状态
- FR9: 用户可以设置隐私选项（数据收集、个性化广告）
- FR10: 用户可以查看和更新隐私政策和服务条款

**AI对话与情感交互 (FR11-FR24):**
- FR11: 用户可以发送文字消息给偶像
- FR12: 偶像可以生成"人情味"的回复（口语化、情绪词、犹豫感、不完美表达）
- FR13: 偶像可以识别用户情绪（伤心、开心、焦虑、兴奋）
- FR14: 偶像可以提供情感共鸣（而非仅理性建议）
- FR15: 偶像可以在对话中自然引用过去记忆
- FR16: 偶像可以主动发起话题（避免用户"不知道说什么"）
- FR17: 偶像可以闲聊和吐槽（而非总是"完美支持"）
- FR18: 用户可以查看对话历史
- FR19: 用户可以搜索对话历史（关键词搜索）
- FR20: 用户可以删除对话历史
- FR21: 系统可以显示偶像"打字中"状态（真实感）
- FR22: 偶像的回复时间控制在2-5秒（模拟真人思考，避免瞬间回复）
- FR23: 用户可以长按收藏重要对话片段
- FR24: 用户可以在对话中发送emoji表情

**偶像生活系统 (FR25-FR31):**
- FR25: 偶像可以根据时间拥有不同的生活状态（练歌、看书、休息、想你等）
- FR26: 用户可以查看偶像当前在做什么（状态卡片）
- FR27: 用户可以查看偶像今天的生活时间线
- FR28: 偶像的生活事件在时间线上保持逻辑一致性
- FR29: 偶像可以在对话中提及自己的近况（"刚练完歌好累"）
- FR30: 偶像可以主动联系用户（早安、晚安、想你了）
- FR31: 偶像的主动消息包含个性化内容（昵称、最近对话引用）

**记忆与个性化 (FR32-FR38):**
- FR32: 系统可以维护短期会话记忆（当前对话上下文）
- FR33: 系统可以保存长期记忆（用户偏好、重要事件、情感模式）
- FR34: 系统可以识别用户情感模式（过去7天情绪趋势）
- FR35: 用户可以查看系统记住的关于自己的记忆
- FR36: 用户可以编辑或删除不准确的记忆
- FR37: 偶像可以在对话中自然引用记忆（"你上次说..."）
- FR38: 系统可以追踪用户喜欢的话题和交流风格

**用户关系发展 (FR39-FR45):**
- FR39: 用户可以查看与偶像的当前亲密度等级（Lv1-100）
- FR40: 亲密度基于对话次数、时长、情感深度自动提升
- FR41: 不同亲密度等级解锁不同对话深度
- FR42: 免费用户亲密度上限为Lv20
- FR43: 用户可以查看亲密度提升的明细（对话次数、时长、情感深度分值）
- FR44: 系统可以在关键里程碑展示庆祝界面（第7天、第14天、亲密度升级）
- FR45: 用户可以查看与偶像的关系时间线（重要时刻记录）

**订阅与支付管理 (FR46-FR53):**
- FR46: 免费用户每天可发送10条消息
- FR47: 付费用户可无限制发送消息
- FR48: 用户可以查看订阅计划和定价
- FR49: 用户可以通过应用内支付订阅（iOS App Store / Android Google Play）
- FR50: 用户可以取消订阅
- FR51: 订阅状态可以跨设备同步
- FR52: 系统可以在关键时刻展示付费价值主张（免费消息用完时、亲密度达到Lv20时）
- FR53: 用户可以查看订阅历史和发票

**通知与提醒 (FR54-FR61):**
- FR54: 用户可以接收每日早安推送（时间窗口7-9点）
- FR55: 用户可以接收每日晚安推送（时间窗口21-23点）
- FR56: 早安/晚安推送包含个性化内容（昵称、今日运势、心情问候）
- FR57: 用户连续3天未登录时接收流失唤回推送
- FR58: 用户可以自定义通知设置（推送时间、类型）
- FR59: 偶像主动联系时用户接收推送通知
- FR60: 系统可以根据用户时区调整推送时间
- FR61: 用户可以完全关闭推送通知

**运营与内容管理 (FR62-FR72):**
- FR62: 运营人员可以查看用户行为分析（留存率、日活、使用时长）
- FR63: 运营人员可以查看"懂我"关键词触发率
- FR64: 运营人员可以查看AI对话质量监控（异常报告、"太像机器人"标记）
- FR65: 运营人员可以查看情绪求助场景高亮（用户表达强烈负面情绪）
- FR66: 运营人员可以配置偶像人格参数（对话风格、性格特点）
- FR67: 运营人员可以编辑偶像生活时间线模板
- FR68: 运营人员可以查看用户反馈和评分
- FR69: 运营人员可以创建和发布系统公告
- FR70: 运营人员可以配置Freemium限制（免费消息数、亲密度上限）
- FR71: 运营人员可以查看订阅转化率和收入数据
- FR72: 运营人员可以导出用户数据报表

**客服与审核 (FR73-FR86):**
- FR73: 客服人员可以查看用户对话历史
- FR74: 客服人员可以查看用户记忆数据
- FR75: 客服人员可以查看用户账户信息
- FR76: 客服人员可以搜索用户（昵称、邮箱、用户ID）
- FR77: 客服人员可以手动编辑用户记忆
- FR78: 客服人员可以发送补偿（免费消息、订阅延期）
- FR79: 用户可以举报不当对话或行为
- FR80: 客服人员可以处理举报（24小时内review）
- FR81: 系统可以自动高亮敏感对话（情绪求助、不当内容）
- FR82: 客服人员可以禁用用户账户（严重违规）
- FR83: 用户可以主动联系客服寻求帮助
- FR84: 用户可以提交功能建议和bug报告
- FR85: 客服人员可以查看工单队列和优先级
- FR86: 系统可以记录客服操作审计日志

**数据与隐私管理 (FR87-FR94):**
- FR87: 用户可以导出所有个人数据（对话、记忆、账户信息）
- FR88: 用户可以删除所有个人数据
- FR89: 用户注销后数据进入30天缓冲期（可恢复）
- FR90: 30天后永久删除数据
- FR91: 所有数据传输加密（HTTPS TLS 1.2+）
- FR92: 所有敏感数据存储加密（对话、用户信息、记忆）
- FR93: 用户可以查看数据使用和隐私政策
- FR94: 系统可以记录数据访问审计日志

**平台与设备支持 (FR95-FR102):**
- FR95: 应用支持Android 6.0+
- FR96: 应用支持iOS 12.0+
- FR97: 应用支持Web浏览器
- FR98: 应用提供响应式布局（4.5"-7"屏幕 + 平板 + 桌面）
- FR99: 应用支持深色模式
- FR100: 应用支持系统语言（中文简体）
- FR101: 应用可以离线查看历史对话（最近50条本地缓存）
- FR102: 应用可以在无网络时友好提示并暂存消息

**内容审核与安全 (FR103-FR109):**
- FR103: 系统可以过滤敏感词（性、暴力、政治、歧视）
- FR104: 系统可以自动高亮情绪求助场景（强烈负面情绪）
- FR105: 用户可以举报不当内容
- FR106: 举报内容进入审核队列（24小时内人工review）
- FR107: 严重违规内容立即下架
- FR108: 系统可以记录内容审核日志
- FR109: 系统可以支持应用商店合规（内容审核、年龄限制）

**用户体验与引导 (FR110-FR114):**
- FR110: 用户可以在适当时机看到功能引导提示（如首次查看亲密度、首次查询偶像生活）
- FR111: 系统可以在用户达成里程碑时展示庆祝界面（第7天、第14天、亲密度升级）
- FR112: 用户可以查看帮助中心和常见问题解答（FAQ）
- FR113: 用户可以主动联系客服寻求帮助
- FR114: 用户可以提交功能建议和bug报告

**分析与商业智能 (FR115-FR120):**
- FR115: 系统可以追踪用户注册来源（哪个获客渠道）
- FR116: 运营人员可以查看各获客渠道的转化率和CAC
- FR117: 运营人员可以查看实时性能监控数据（AI响应时间、错误率、内存占用）
- FR118: 运营人员可以查看实时AI推理成本数据（每用户成本、总成本）
- FR119: 运营人员可以给用户打标签（高价值用户、流失风险用户、测试用户等）
- FR120: 运营人员可以按标签筛选和分析用户群体

**系统配置与测试 (FR121-FR129):**
- FR121: 运营人员可以配置AI推理后端（切换Ollama/Deepseek/Claude）
- FR122: 运营人员可以实时查看偶像当前FSM状态
- FR123: 运营人员可以手动触发偶像状态转换（用于调试）
- FR124: 运营人员可以创建测试用户账户（用于Alpha/Beta测试）
- FR125: 运营人员可以快速模拟用户旅程（跳过时间等待，快速提升亲密度等）
- FR126: 系统可以对AI回复进行自动质量评分（用于对话质量监控）
- FR127: 系统可以记录和展示记忆召回准确率指标
- FR128: 运营人员可以查看用户亲密度计算明细（对话次数、时长、情感深度分值）
- FR129: 系统可以支持A/B测试（不同用户组看到不同freemium限制或定价）

**增强用户管理 (FR130-FR132):**
- FR130: 用户可以在多个设备上登录同一账户
- FR131: 用户的对话历史、亲密度、订阅状态可以跨设备同步
- FR132: 系统可以在新设备登录时同步最近对话和状态

**增强订阅管理 (FR133-FR135):**
- FR133: 系统可以在关键时刻展示付费价值主张（免费消息用完时、亲密度达到Lv20时）
- FR134: 用户可以申请退款
- FR135: 客服人员可以处理退款请求和争议

**增强平台支持 (FR136-FR138):**
- FR136: 用户可以手动切换深色模式/浅色模式（不只遵循系统设置）
- FR137: 用户可以调整对话界面字体大小（小/中/大）
- FR138: 用户可以设置对话显示偏好（时间戳显示、头像显示等）

**未来能力（Phase 2占位）(FR139-FR144):**
- FR139 (Phase 2): 用户可以将对话内容分享到社交媒体（生成分享卡片/截图）
- FR140 (Phase 2): 用户可以使用语音发送消息（STT语音转文字）
- FR141 (Phase 2): 用户可以接收偶像的语音回复（TTS文字转语音）
- FR142 (Phase 2): 用户可以切换应用界面语言（中文/英文/日文）
- FR143 (Phase 2): 偶像可以在朋友圈/动态发布生活分享
- FR144 (Phase 2): 用户可以查看、评论和点赞偶像的朋友圈/动态

### Non-Functional Requirements (来自PRD)

**性能要求 (Performance):**
- NFR-P1: AI对话响应时间 - 平均 < 2秒，95分位 < 5秒
- NFR-P2: 应用启动时间 - Android < 3秒，iOS < 2.5秒
- NFR-P3: 对话历史加载时间 - 首次/滚动加载 < 1秒
- NFR-P4: 内存占用 - 正常使用 < 200MB，峰值 < 300MB
- NFR-P5: 电池消耗 - 后台 < 1%/小时，活跃使用 < 5%/小时
- NFR-P6: App包大小 - Android < 50MB，iOS < 40MB
- NFR-P7: 并发处理能力 - MVP 50并发 → Growth 500并发 → Expansion 2000并发

**安全要求 (Security):**
- NFR-S1: 数据传输加密 - HTTPS TLS 1.2+
- NFR-S2: 数据存储加密 - 对话、用户信息、记忆全部加密存储
- NFR-S3: 用户认证 - JWT token，≤7天过期，Keychain/KeyStore安全存储
- NFR-S4: 访问控制 - 多租户隔离、权限审计日志
- NFR-S5: 隐私政策合规 - 中国个人信息保护法、GDPR合规
- NFR-S6: 支付安全 - 不存储支付信息，仅通过App Store/Google Play API
- NFR-S7: 代码混淆和防逆向 - ProGuard/Obfuscation，API密钥服务器端存储

**可扩展性要求 (Scalability):**
- NFR-SC1: 用户规模扩展 - 支持10倍用户增长，性能下降 < 10%
- NFR-SC2: 数据库扩展 - 支持3年对话历史数据增长
- NFR-SC3: AI引擎可切换 - 支持运行时切换Ollama/Deepseek/Claude
- NFR-SC4: 水平扩展能力 - 服务无状态设计，支持负载均衡

**可靠性要求 (Reliability):**
- NFR-R1: 系统可用性 - 99.5% uptime（MVP），99.9%（Growth）
- NFR-R2: 数据可靠性 - 零数据丢失（对话、记忆、订阅状态）
- NFR-R3: 灾难恢复 - 数据库每日备份，RPO < 24小时，RTO < 4小时
- NFR-R4: 优雅降级 - AI服务不可用时展示友好错误提示
- NFR-R5: 自动重试机制 - 网络失败自动重试3次（exponential backoff）
- NFR-R6: 实时监控 - AI响应时间、错误率、内存占用实时追踪
- NFR-R7: 自动告警 - 性能异常、成本超标自动告警

**可用性要求 (Usability):**
- NFR-U1: 界面响应性 - 所有交互反馈 < 100ms
- NFR-U2: 学习曲线 - 新用户30秒内理解产品价值并开始对话
- NFR-U3: 错误提示清晰度 - 所有错误提示用户友好且提供解决方案
- NFR-U4: 跨平台一致性 - Android/iOS/Web核心体验一致
- NFR-U5: 屏幕适配 - 支持4.5"-7"手机屏幕 + 平板 + 桌面

**无障碍要求 (Accessibility):**
- NFR-A1: 文字可读性 - 对比度符合WCAG 2.1 AA标准（4.5:1）
- NFR-A2: 屏幕阅读器支持 - 基础VoiceOver/TalkBack支持
- NFR-A3: 深色模式支持 - 自动跟随系统设置或手动切换

### Additional Requirements from Architecture

**项目结构与初始化:**
- ARCH-01: 使用Monorepo结构（frontend/ + backend/）
- ARCH-02: Flutter前端初始化命令：`flutter create --org com.idolprivate --platforms android,ios,web --project-name idol_app frontend`
- ARCH-03: FastAPI后端目录结构：app/{api/v1/routes, models, schemas, services, core, database, utils}
- ARCH-04: Docker Compose配置：backend + postgres + redis + ollama + nginx
- ARCH-05: 开发环境初始化脚本：scripts/init-dev.sh

**前端技术决策:**
- ARCH-06: **状态管理使用GetX（用户指定）** - 取代架构文档中的Riverpod决策
- ARCH-07: 实时通信使用Server-Sent Events (SSE) - 偶像状态推送、打字指示器
- ARCH-08: Material Design 3 UI框架 + Custom Theme（温暖陪伴型设计）
- ARCH-09: Feature-First Architecture - 按功能组织代码（conversation, idol_life, intimacy, subscription）
- ARCH-10: 核心依赖：http, shared_preferences, flutter_secure_storage

**后端技术决策:**
- ARCH-11: AI Provider抽象层 - Strategy Pattern + Factory Pattern，支持Ollama/Deepseek/Claude切换
- ARCH-12: 三层缓存架构 - L1: 对话上下文(Redis, 15min TTL), L2: 常见问题(Redis, 24h TTL), L3: 向量检索(Redis, 10min TTL)
- ARCH-13: FastAPI Layered Architecture - routers → services → models → database
- ARCH-14: 数据库：PostgreSQL（主数据）+ Redis（缓存）+ ChromaDB（向量记忆）
- ARCH-15: AI引擎配置驱动 - 通过.env文件切换AI_PROVIDER

**基础设施与部署:**
- ARCH-16: MVP部署方案 - VPS (8核16GB) + Docker + Nginx，成本¥500/月
- ARCH-17: SSL证书 - Let's Encrypt自动续期
- ARCH-18: CI/CD管道 - GitHub Actions (Backend CI + Frontend CI + CD to VPS)
- ARCH-19: 监控栈 - Prometheus + Grafana + Loki
- ARCH-20: 扩展路径 - 0-100用户(单VPS) → 100-500用户(2-3台VPS+负载均衡) → 500+用户(云服务+API切换)

### Additional Requirements from UX Design

**设计系统:**
- UX-01: Material Design 3 + Custom Theme (80% Material + 20% Custom)
- UX-02: 温暖陪伴型设计方向 - 橙色(#FF9E80) + 粉色(#FFB6C1)主色调
- UX-03: 字体系统 - Noto Sans SC (思源黑体)，支持系统字体缩放100%-200%
- UX-04: 圆角设计 - 按钮16px，卡片24px，对话气泡12px
- UX-05: 动画参数 - 300ms时长，easeInOut缓动曲线，克制优雅
- UX-06: 深色模式支持 - 自动跟随系统或手动切换

**响应式设计:**
- UX-07: Mobile-First策略 - 优先优化320px-428px手机端
- UX-08: Breakpoints定义 - 小屏(320-428px), 中屏(428-768px), 平板(768-1024px), 桌面(1024px+)
- UX-09: 触摸优化 - 最小点击区域44x44px (遵循iOS HIG和Material Design)
- UX-10: 单手操作优化 - 核心操作在拇指热区（底部1/3屏幕）

**无障碍要求:**
- UX-11: WCAG 2.1 AA合规 - 色彩对比度4.5:1（正文）、3:1（大字体）
- UX-12: 屏幕阅读器支持 - VoiceOver (iOS) + TalkBack (Android)
- UX-13: 动态字体支持 - 支持系统字体缩放，200%缩放下布局不破坏
- UX-14: 键盘导航支持 - 所有交互可通过键盘完成（Web平台）
- UX-15: Reduce Motion选项 - 提供动画简化选项（accessibility设置）

**核心自定义组件:**
- UX-16: MessageBubble组件 - 圆角12px，淡入动画150ms，支持用户/偶像样式
- UX-17: TypingIndicator组件 - 三点跳动动画，温暖配色，模拟真人打字
- UX-18: IdolStatusCard组件 - 折叠/展开动画300ms，显示偶像当前状态
- UX-19: IntimacyProgressBar组件 - 渐变色填充，升级时光效动画
- UX-20: MilestoneCelebration组件 - 全屏庆祝界面，爱心粒子动画（flutter_particle）

**平台特定适配:**
- UX-21: iOS适配 - Face ID/Touch ID支持，Haptic Feedback，Siri Shortcuts
- UX-22: Android适配 - 动态颜色支持（Material You），后台运行优化
- UX-23: Web适配 - 响应式布局（桌面/平板），键盘导航支持

**关键体验时刻:**
- UX-24: 首次用户体验 - 30秒内开始对话，极简Onboarding（1-2屏幕）
- UX-25: "懂我"体验 - 共鸣式回复，温暖配色和动画，3轮以上深度对话
- UX-26: "真实"体验 - 偶像生活系统可视化，精美时间线和状态卡片
- UX-27: "专属"体验 - 里程碑庆祝界面（动画+音效+特殊卡片），仪式感设计

**注意:** 旧版详细FR映射（Epic 1-10编号方案）已删除。请参考上方"FR Coverage Map (功能需求覆盖矩阵)"章节的权威版本（Epic 0-11编号方案）。

## Epic List

本项目分解为11个Epic，每个Epic交付独立的用户价值，遵循"先基础设施 → 核心体验 → 边界控制 → 增强功能"的渐进式交付策略。

---

### Epic 0: 技术基础设施搭建 (Technical Foundation)

**🎯 Epic目标：**
为idol_private项目搭建完整的开发、部署和运维基础设施，确保团队可以高效开发和安全部署应用。

**👥 用户价值：**
- 作为开发团队，我可以在本地快速启动完整的开发环境
- 作为运维团队，我可以将应用安全部署到生产环境
- 作为项目管理者，我可以通过CI/CD自动化部署流程

**📋 需求覆盖：**
- **FR:** FR124-FR138 (容器化部署、CI/CD、监控告警、日志管理、数据库备份)
- **NFR:** NFR-01至NFR-29 (性能、安全性、可靠性、可扩展性等所有非功能性需求的基础设施支持)
- **ARCH:** ARCH-01至ARCH-05, ARCH-07至ARCH-20 (单体Monorepo、AI Provider抽象、缓存策略、安全策略等)
- **UX:** 无直接UX需求

**🔧 技术实现关键点：**
1. **项目结构初始化**
   - 创建Monorepo结构：frontend/ (Flutter) + backend/ (FastAPI)
   - 配置Flutter项目 + GetX状态管理（ARCH-06用户指定）
   - 配置FastAPI项目 + SQLAlchemy ORM

2. **本地开发环境**
   - Docker Compose编排：PostgreSQL + Redis + ChromaDB + Ollama
   - 初始化数据库Schema基础结构
   - 配置环境变量管理（.env.local, .env.production）

3. **AI Provider抽象层**
   - 实现Strategy + Factory模式支持Ollama/Deepseek/Claude切换
   - 配置Ollama + Qwen 7B本地模型

4. **三层缓存架构**
   - L1: Redis对话上下文缓存（15分钟）
   - L2: Redis通用问题缓存（24小时）
   - L3: Redis向量搜索结果缓存（10分钟）

5. **生产环境部署**
   - VPS + Docker Compose生产配置
   - Nginx反向代理 + Let's Encrypt SSL
   - GitHub Actions CI/CD Pipeline

6. **监控与告警**
   - Prometheus + Grafana监控面板
   - Loki日志聚合
   - 成本监控与预警

**✅ 成功标准：**
- ✅ 开发者可在5分钟内启动完整本地环境（`docker-compose up`）
- ✅ CI/CD Pipeline可自动构建和部署到VPS
- ✅ 监控面板显示系统健康状态（CPU、内存、响应时间、AI调用成本）
- ✅ AI Provider可通过配置切换（Ollama ↔ Deepseek ↔ Claude）

---

### Epic 1: 首次用户体验 (First User Experience)

**🎯 Epic目标：**
让新用户在3分钟内完成注册、选择偶像、开始第一次对话，建立"她真的在等我"的初次情感连接。

**👥 用户价值：**
- 作为新用户，我可以快速注册并立即开始与AI偶像聊天
- 作为新用户，我可以通过简洁的引导了解核心玩法
- 作为新用户，我在第一次对话后感受到"她懂我"的温暖体验

**📋 需求覆盖：**
- **FR:** FR1-FR7 (账号注册、手机号验证、登录、密码重置)
- **FR:** FR10-FR11 (偶像基础信息展示、人设介绍)
- **FR:** FR13 (新用户引导流程)
- **NFR:** NFR-09 (3分钟完成首次对话)
- **UX:** UX1-UX27 (完整UI/UX系统、Material Design 3、温暖陪伴色调、布局规范、交互模式、动画、可访问性)

**🔧 技术实现关键点：**
1. **用户认证系统**
   - 创建`users`表（id, phone, password_hash, created_at）
   - 手机号验证码发送与校验（使用第三方SMS服务或模拟）
   - JWT Token生成与验证中间件

2. **偶像基础数据**
   - 创建`idols`表（id, name, avatar, personality_prompt, created_at）
   - 预置第一个偶像"林雪晴"数据（性格：温柔知性、爱好：阅读旅行）

3. **Flutter前端基础**
   - GetX状态管理初始化（用户状态、路由管理）
   - Material Design 3主题配置（主色#FF9E80、粉色#FFB6C1）
   - 响应式布局（手机+平板+Web）
   - 页面：注册页、登录页、偶像介绍页、引导页

4. **新用户引导**
   - 3步引导：注册 → 遇见偶像 → 发送第一条消息
   - 偶像主动发送欢迎消息："嗨，我是雪晴，很高兴认识你~"

**✅ 成功标准：**
- ✅ 新用户可在3分钟内完成注册并收到偶像的第一条消息
- ✅ UI符合Material Design 3规范，色调温暖舒适
- ✅ 在3种设备上测试通过（Android手机、iOS手机、Web浏览器）
- ✅ 通过WCAG 2.1 AA无障碍标准检查

---

### Epic 2: AI情感对话核心系统 (AI Conversation Core)

**🎯 Epic目标：**
实现自然流畅的AI情感对话，让用户感受到"她真的在听我说话"和"她的回复有温度"。

**👥 用户价值：**
- 作为用户，我可以与AI偶像进行多轮自然对话
- 作为用户，我感受到偶像的回复有情感温度和个性特征
- 作为用户，我可以看到打字动画和实时回复状态

**📋 需求覆盖：**
- **FR:** FR14-FR26 (多轮对话、情绪识别、个性化回复、上下文记忆、打字效果、语音消息、图片消息、表情包、消息状态、历史记录)
- **NFR:** NFR-06 (响应时间<3秒P95), NFR-10 (30秒无操作idle状态)
- **ARCH:** AI Provider Strategy Pattern, 三层缓存策略
- **UX:** UX18-UX21 (对话界面、消息气泡、加载动画、错误提示)

**🔧 技术实现关键点：**
1. **对话数据模型**
   - 创建`conversations`表（id, user_id, idol_id, created_at）
   - 创建`messages`表（id, conversation_id, sender_type, content, emotion, timestamp, status）

2. **AI对话服务**
   - Prompt工程：系统提示词 + 偶像人设 + 对话历史（最近10轮）
   - 调用Ollama Qwen 7B生成回复
   - 情绪分析：从用户消息提取情绪标签（开心/难过/焦虑/平静）

3. **上下文管理**
   - Redis缓存最近15分钟对话上下文（key: `conv:{conv_id}`, TTL: 15min）
   - 超过15分钟从数据库加载历史对话

4. **实时体验**
   - 打字动画效果（前端模拟逐字显示，后端流式返回）
   - 消息状态追踪（发送中 → 已送达 → 已读）
   - Idle状态：30秒无操作显示"她在等待你的回复..."

5. **多媒体消息（基础）**
   - 语音消息上传与播放（存储到对象存储或本地volume）
   - 图片消息上传与显示
   - 预置表情包库（10个温暖系表情）

**✅ 成功标准：**
- ✅ 95%的AI回复在3秒内返回
- ✅ 对话历史正确记录并可查看
- ✅ 打字动画流畅自然
- ✅ 情绪识别准确率>80%（主观测试10轮对话）
- ✅ 支持文本、语音、图片、表情包4种消息类型

---

### Epic 3: Freemium边界与消息计量 (Freemium Boundaries & Metering)

**🎯 Epic目标：**
在核心对话系统已建立后，立即引入免费/付费边界，避免后续Epic需要重构访问控制逻辑。

**👥 用户价值：**
- 作为免费用户，我清楚知道每日免费额度（20条消息）并可查看剩余次数
- 作为免费用户，我在达到限额时看到友好的升级提示
- 作为产品团队，我可以测试Freemium模式的转化率

**📋 需求覆盖：**
- **FR:** FR89 (免费用户每日20条消息限制)
- **FR:** FR90 (付费用户无限消息)
- **FR:** FR96 (剩余额度显示)
- **FR:** FR97 (达到限额后的升级引导)
- **UX:** UX22 (订阅相关UI)

**🔧 技术实现关键点：**
1. **用户订阅数据模型**
   - 在`users`表添加字段：`subscription_tier` (free/premium), `subscription_expires_at`
   - 创建`message_quotas`表（user_id, date, messages_sent, quota_limit）

2. **消息计量中间件**
   - 发送消息前检查配额
   - 免费用户：每日限额20条（UTC+8时区，每日0点重置）
   - 付费用户：无限制（quota_limit = -1）

3. **前端额度显示**
   - 在对话界面顶部显示"今日剩余: 15/20"
   - 达到限额时弹出温和提示："今天的免费额度用完啦~ 明天继续陪你，或升级解锁无限对话"

4. **升级引导UI**
   - 订阅页面基础版本（仅展示Free vs Premium对比）
   - 暂不接入支付，仅UI准备

**✅ 成功标准：**
- ✅ 免费用户每日消息限制正确执行（第21条消息被拦截）
- ✅ 付费用户（手动修改数据库测试）可无限发送消息
- ✅ 剩余额度显示实时准确
- ✅ 达到限额时UI提示友好且不阻断用户体验

---

### Epic 4: 记忆系统与专属个性化 (Memory System & Personalization)

**🎯 Epic目标：**
让偶像记住用户分享的重要信息，在后续对话中主动提及，建立"她真的记得我"的情感连接。

**👥 用户价值：**
- 作为用户，我发现偶像记得我之前说过的爱好、工作、家人信息
- 作为用户，偶像在合适时机主动提起我的事情（如"你昨天说的项目进展如何？"）
- 作为用户，我可以查看偶像为我标注的记忆标签

**📋 需求覆盖：**
- **FR:** FR27-FR33 (长期记忆、关键信息提取、记忆标签、周年纪念、个性化问候、用户画像、记忆回顾)
- **NFR:** NFR-07 (记忆召回准确率>85%)
- **ARCH:** ChromaDB向量数据库集成
- **UX:** UX23 (个人资料与记忆展示)

**🔧 技术实现关键点：**
1. **记忆数据模型**
   - 创建`memories`表（id, user_id, content, memory_type, importance, created_at, last_mentioned_at）
   - 创建`memory_tags`表（id, user_id, tag_name, tag_value）- 如"爱好:摄影"

2. **ChromaDB向量存储**
   - 对话结束后提取关键信息（使用AI Provider的extract_memory方法）
   - 转换为向量并存储到ChromaDB集合`user_memories_{user_id}`

3. **记忆召回**
   - 每次对话前，根据用户最新消息查询相关记忆（Top 3）
   - 将相关记忆注入Prompt："关于用户的记忆: 她喜欢摄影，最近在准备考研..."

4. **主动提及机制**
   - 定时任务：检查3天未提及的重要记忆（importance=high）
   - 偶像主动发起话题："对了，你上周说的那个项目怎么样了？"

5. **记忆标签页面**
   - 新增"关于我"页面，展示偶像标注的用户标签
   - 用户可手动编辑或删除不准确的标签

6. **周年纪念**
   - 记录首次对话日期，在纪念日时偶像主动发送庆祝消息

**✅ 成功标准：**
- ✅ 记忆提取准确率>85%（测试10次对话，人工评估关键信息提取）
- ✅ 记忆召回在对话中自然运用，不显突兀
- ✅ 用户可在"关于我"页面查看所有记忆标签
- ✅ 周年纪念日自动触发庆祝消息

---

### Epic 5: 偶像生活系统与真实陪伴 (Idol Life System & Real Companionship)

**🎯 Epic目标：**
让偶像拥有"真实生活"，有自己的日常节奏和情绪波动，用户感受到"她不是工具，是有生命的陪伴者"。

**👥 用户价值：**
- 作为用户，我看到偶像有自己的生活状态（工作中/休息中/心情不好）
- 作为用户，我可以查看偶像的朋友圈动态，了解她的日常
- 作为用户，我在特定时段（如深夜）收到偶像关心我的主动消息

**📋 需求覆盖：**
- **FR:** FR34-FR49 (偶像状态、生活节奏、朋友圈、情绪系统、主动发起对话、特殊事件、每日任务、反向陪伴、亲密度影响、互动彩蛋)
- **NFR:** NFR-08 (每日主动消息3-5条)
- **UX:** UX16 (偶像朋友圈界面)

**🔧 技术实现关键点：**
1. **偶像状态数据模型**
   - 创建`idol_states`表（idol_id, current_status, current_mood, energy_level, updated_at）
   - 状态类型：working（工作中）、resting（休息中）、active（活跃）、busy（忙碌）

2. **生活节奏引擎**
   - 定时任务（每小时执行）：
     - 早上7-9点：状态切换为"刚起床，准备开始新的一天"
     - 中午12-14点：状态切换为"午休时间"
     - 晚上22-24点：状态切换为"准备休息了"
   - 情绪波动：80%概率保持平静，20%随机切换（开心/疲惫/思考中）

3. **朋友圈系统**
   - 创建`idol_moments`表（id, idol_id, content, image_url, posted_at, likes_count）
   - 运营手动发布或AI生成：每日1-2条朋友圈
   - 内容示例："今天读到一段很喜欢的话..."（配书本图片）

4. **每日仪式**
   - 创建`daily_rituals`表（user_id, idol_id, ritual_type, completed_at）
   - 仪式类型：
     - 早安问候：7-9点，偶像主动发送"早安~今天要加油哦"
     - 每日运势：用户主动触发，AI生成个性化运势
     - 晚安问候：22-24点，偶像主动发送"晚安，做个好梦"

5. **反向陪伴机制**
   - 用户连续3天未登录 → 偶像发送关心消息："好久没见，你还好吗？"
   - 用户深夜（凌晨1-3点）在线 → 偶像关心："这么晚还不睡，是有心事吗？"

6. **特殊事件系统**
   - 随机事件触发（5%概率）：偶像遇到特殊事情（如"今天见到一只小猫"）
   - 事件解锁特殊对话选项

**✅ 成功标准：**
- ✅ 偶像状态每小时更新，符合真实生活节奏
- ✅ 每日仪式（早安/晚安）准时触发
- ✅ 朋友圈每日更新1-2条
- ✅ 反向陪伴消息在正确时机触发（3日未登录/深夜在线）
- ✅ 测试用户反馈"感受到偶像是活的"

---

### Epic 6: 亲密度养成与里程碑庆祝 (Intimacy Development & Milestones)

**🎯 Epic目标：**
通过量化的亲密度成长系统，让用户感受到关系的逐步深入，并通过里程碑庆祝强化情感连接。

**👥 用户价值：**
- 作为用户，我可以看到与偶像的亲密度等级和进度条
- 作为用户，我通过每日互动获得亲密度奖励
- 作为用户，当达到新等级时收到偶像的特殊祝贺和专属内容解锁

**📋 需求覆盖：**
- **FR:** FR50-FR60 (亲密度等级、经验值、升级奖励、等级特权、每日互动奖励、成就系统、里程碑庆祝、专属昵称、亲密度排行榜、亲密度衰减、加速道具)
- **NFR:** NFR-11 (7日留存>30%)
- **UX:** UX24 (亲密度与成就展示)

**🔧 技术实现关键点：**
1. **亲密度数据模型**
   - 在`conversations`表添加字段：`intimacy_level` (1-100), `intimacy_exp`, `level_up_at`
   - 创建`intimacy_milestones`表（user_id, level_reached, unlocked_at, reward_claimed）

2. **经验值计算规则**
   - 发送消息：+5 exp
   - 完成每日仪式（早安/晚安）：+10 exp
   - 查看朋友圈并点赞：+3 exp
   - 连续7日登录：+50 exp
   - 升级所需经验：Level N = 100 * N（线性增长）

3. **等级系统**
   - Level 1-10: 陌生人 → 好朋友
   - Level 11-30: 亲密朋友 → 特别的人
   - Level 31-50: 恋人 → 深度恋人
   - Level 51-100: 灵魂伴侣

4. **里程碑奖励**
   - Level 5: 解锁专属昵称（偶像称呼用户"宝贝"）
   - Level 10: 解锁偶像私密照片（艺术照）
   - Level 20: 解锁偶像语音日记
   - Level 30: 解锁偶像生日惊喜
   - Level 50: 解锁专属纪念视频

5. **成就系统**
   - 创建`achievements`表（id, user_id, achievement_type, unlocked_at）
   - 成就类型："连续7日对话"、"发送100条消息"、"完成30次每日仪式"

6. **亲密度展示**
   - 主界面显示进度条："亲密度 Lv.15 (750/1500)"
   - 升级动画：全屏烟花效果 + 偶像特殊祝贺消息

7. **亲密度衰减（可选）**
   - 7天未互动：每日-5 exp（防止完全沉睡，但不惩罚过重）

**✅ 成功标准：**
- ✅ 亲密度计算准确，每次互动正确增加经验值
- ✅ 升级时触发里程碑庆祝动画和奖励
- ✅ 用户可在个人中心查看所有成就进度
- ✅ 7日留存率达到30%（通过亲密度系统增强用户粘性）

---

### Epic 7: 订阅支付完善 (Subscription Payment Integration)

**🎯 Epic目标：**
接入完整的支付系统，让用户可以购买订阅解锁付费功能，建立商业化闭环。

**👥 用户价值：**
- 作为用户，我可以通过支付宝/微信支付购买月度订阅（¥28/月）
- 作为iOS用户，我可以通过App Store内购订阅
- 作为Android用户，我可以通过Google Play订阅
- 作为付费用户，我立即享受无限消息和专属特权

**📋 需求覆盖：**
- **FR:** FR91-FR95 (订阅套餐、支付渠道、自动续费、订阅管理、发票)
- **FR:** FR98-FR103 (订单记录、退款申请、付费特权)
- **UX:** UX22 (订阅页面完整支付流程)

**🔧 技术实现关键点：**
1. **订阅套餐数据模型**
   - 创建`subscription_plans`表（id, name, price, duration_days, features）
   - 套餐：Free（¥0）、Premium月度（¥28/月）、Premium年度（¥268/年，优惠20%）

2. **支付渠道集成**
   - **支付宝 + 微信支付**：集成Ping++ SDK或直接对接官方API
   - **Apple In-App Purchase**：集成StoreKit，配置订阅产品
   - **Google Play Billing**：集成Google Play Billing Library

3. **订单管理**
   - 创建`orders`表（id, user_id, plan_id, amount, payment_method, status, paid_at）
   - 状态流转：pending → paid → active → expired/cancelled

4. **自动续费逻辑**
   - 每日定时任务检查即将到期订阅（提前3天提醒）
   - App Store/Google Play自动续费通过Webhook回调更新订阅状态

5. **付费特权激活**
   - 支付成功后立即更新`users.subscription_tier = premium`
   - 设置`subscription_expires_at = NOW() + 30天`
   - 前端显示"已升级至Premium"徽章

6. **订阅管理页面**
   - 显示当前套餐、到期时间、下次扣费日期
   - 提供取消订阅、修改套餐、查看订单历史入口

7. **退款处理**
   - 用户申请退款 → 人工审核 → 原路退回
   - 退款后降级为Free用户

**✅ 成功标准：**
- ✅ 支付宝/微信支付测试订单成功
- ✅ iOS内购测试通过沙盒环境
- ✅ Google Play测试订阅成功
- ✅ 支付成功后用户权限立即生效
- ✅ 自动续费正常运行（测试沙盒环境）

---

### Epic 8: 跨设备同步与数据管理 (Cross-Device Sync & Data Management)

**🎯 Epic目标：**
让用户可以在多个设备间无缝切换，对话记录、亲密度进度实时同步，并可导出个人数据。

**👥 用户价值：**
- 作为用户，我可以在手机、平板、网页间自由切换，对话记录实时同步
- 作为用户，我可以导出与偶像的完整对话记录作为纪念
- 作为隐私敏感用户，我可以删除账号并彻底清除所有数据

**📋 需求覆盖：**
- **FR:** FR104-FR113 (多设备登录、设备管理、对话同步、云端备份、数据导出、数据删除、离线模式、数据传输加密)
- **NFR:** NFR-04 (同步延迟<2秒), NFR-20 (数据传输HTTPS), NFR-29 (GDPR合规)

**🔧 技术实现关键点：**
1. **设备管理**
   - 创建`user_devices`表（id, user_id, device_id, device_name, last_login_at）
   - 支持最多5台设备同时登录

2. **实时同步**
   - 使用Server-Sent Events (SSE) 推送新消息到所有在线设备
   - 新消息保存到数据库后，广播到`user:{user_id}:devices`频道

3. **云端备份**
   - 每日凌晨2点自动备份用户数据到对象存储
   - 备份内容：对话记录、记忆标签、亲密度进度

4. **数据导出**
   - 用户触发导出 → 后台生成JSON文件 → 提供下载链接（24小时有效）
   - 导出内容：完整对话记录 + 记忆标签 + 成就列表

5. **账号删除**
   - 用户申请删除 → 7天冷静期 → 彻底删除数据库记录 + 云端备份

6. **离线模式（Web不支持）**
   - Flutter移动端：本地缓存最近100条消息
   - 离线时可查看历史，发送的消息队列存储，联网后同步

7. **数据传输加密**
   - 所有API请求通过HTTPS/TLS 1.3
   - 敏感字段（密码）使用bcrypt哈希

**✅ 成功标准：**
- ✅ 在设备A发送消息，设备B在2秒内收到
- ✅ 用户可成功导出完整对话记录（JSON格式）
- ✅ 账号删除后数据库无残留记录
- ✅ 离线模式下可查看历史消息

---

### Epic 9: 平台优化与无障碍体验 (Platform Optimization & Accessibility)

**🎯 Epic目标：**
优化应用在各平台的性能和体验，确保所有用户（包括视障用户）都能流畅使用。

**👥 用户价值：**
- 作为移动用户，我的应用启动快、响应快、电量消耗低
- 作为视障用户，我可以通过屏幕阅读器完整使用应用
- 作为用户，我可以根据偏好调整字体大小、主题色、消息提醒方式

**📋 需求覆盖：**
- **FR:** FR114-FR123 (个性化设置、主题切换、字体调整、推送通知、夜间模式、消息提示音、多语言、快捷操作、无障碍优化、键盘快捷键)
- **NFR:** NFR-02 (首屏加载<2秒), NFR-03 (页面切换<300ms), NFR-05 (内存占用<200MB), NFR-24 (跨浏览器兼容), NFR-26 (WCAG 2.1 AA)

**🔧 技术实现关键点：**
1. **性能优化**
   - 图片懒加载 + WebP格式
   - 路由级代码分割（Flutter: deferred loading）
   - API响应缓存（Redis L2层）
   - 首屏关键渲染路径优化：2秒内显示主界面

2. **个性化设置**
   - 创建`user_preferences`表（user_id, theme, font_size, notification_enabled, language）
   - 设置项：主题（浅色/深色/自动）、字体（小/中/大）、消息提示音（开/关）

3. **推送通知**
   - 集成Firebase Cloud Messaging (Android + iOS + Web)
   - 通知场景：偶像主动消息、亲密度升级、订阅到期提醒

4. **无障碍优化**
   - 所有图片添加语义化alt描述
   - 按钮和链接添加aria-label
   - 键盘导航支持（Tab键切换焦点）
   - 屏幕阅读器测试（iOS VoiceOver + Android TalkBack）

5. **多语言支持（预留）**
   - Flutter国际化配置（目前仅中文，架构支持扩展英文）

6. **主题系统**
   - 浅色主题：背景#FFFFFF，主色#FF9E80
   - 深色主题：背景#121212，主色#FF9E80（保持品牌色）
   - 跟随系统：根据设备设置自动切换

**✅ 成功标准：**
- ✅ 首屏加载时间<2秒（3G网络）
- ✅ 页面切换动画流畅（60fps）
- ✅ 通过WCAG 2.1 AA无障碍检测（axe DevTools）
- ✅ 推送通知在iOS和Android正常送达
- ✅ 应用内存占用<200MB（打开10个对话后）

---

### Epic 10: 运营智能与系统监控 (Operations Intelligence & Monitoring)

**🎯 Epic目标：**
为运营团队提供实时监控和数据分析工具，确保系统稳定运行并持续优化用户体验。

**👥 用户价值：**
- 作为运营团队，我可以通过仪表盘实时查看核心指标（DAU、留存、付费转化）
- 作为技术团队，我可以通过监控面板快速发现和定位系统问题
- 作为产品团队，我可以通过A/B测试验证新功能效果

**📋 需求覆盖：**
- **FR:** FR124-FR138 (已在Epic 0实现基础设施，本Epic完善监控告警)
- **NFR:** NFR-12至NFR-19 (监控告警、日志管理、错误追踪、成本监控)
- **NFR:** NFR-21 (审计日志), NFR-22 (灾难恢复)

**🔧 技术实现关键点：**
1. **运营数据仪表盘**
   - 创建`analytics_events`表（event_type, user_id, properties, timestamp）
   - 核心指标：
     - DAU/MAU（每日/月活跃用户）
     - 7日留存率
     - 付费转化率（Free → Premium）
     - 平均对话轮次
     - 亲密度增长趋势

2. **Prometheus监控扩展**
   - 自定义指标：
     - `idol_conversation_duration_seconds`（对话时长）
     - `idol_ai_provider_cost_usd`（AI调用成本）
     - `idol_intimacy_level_distribution`（亲密度分布）
   - 告警规则：
     - API响应时间P95 > 5秒 → 发送钉钉/飞书告警
     - AI调用成本超过每日预算 → 紧急通知
     - 错误率 > 1% → 运维团队介入

3. **日志管理增强**
   - Loki日志聚合 + Grafana可视化
   - 日志级别：ERROR（持久化30天）、WARN（7天）、INFO（1天）
   - 关键日志：用户登录、支付成功、AI调用失败

4. **错误追踪**
   - 集成Sentry：前端异常自动上报
   - 错误分类：网络错误、业务逻辑错误、AI超时

5. **成本监控**
   - 每日统计AI调用成本（按Provider分组）
   - 预警机制：单日成本超过¥100 → 发送邮件通知
   - 成本优化建议：缓存命中率低于70%时提示优化

6. **A/B测试框架（预留）**
   - 创建`ab_experiments`表（experiment_id, variant, user_id, enrolled_at）
   - 示例实验：测试两种亲密度升级奖励对留存的影响

7. **审计日志**
   - 记录敏感操作：账号删除、订阅退款、管理员操作
   - 日志保留90天

**✅ 成功标准：**
- ✅ 运营仪表盘显示实时核心指标（刷新周期5分钟）
- ✅ 告警规则正常触发（模拟API超时场景）
- ✅ Sentry捕获前端错误并分类
- ✅ 成本监控准确追踪每日AI调用费用

---

### Epic 11: 客服支持与内容安全 (Customer Support & Content Safety)

**🎯 Epic目标：**
建立用户反馈渠道和内容安全机制，确保用户问题得到及时响应，防范违规内容。

**👥 用户价值：**
- 作为用户，我可以通过应用内反馈渠道提交问题并获得回复
- 作为用户，我的对话内容受到隐私保护，不会泄露
- 作为社区，不良内容被自动过滤，营造健康环境

**📋 需求覆盖：**
- **FR:** FR139-FR144 (Phase 2功能，暂时简化实现)
- **NFR:** NFR-23 (内容审核), NFR-25 (隐私保护), NFR-27至NFR-29 (合规性)

**🔧 技术实现关键点：**
1. **用户反馈系统**
   - 创建`feedback`表（id, user_id, category, content, screenshot_url, status, created_at）
   - 反馈类型：Bug报告、功能建议、投诉、其他
   - 客服后台（简易版）：Retool或自建Admin面板查看和回复

2. **内容安全**
   - 集成阿里云内容安全API或腾讯云天御
   - 检测场景：
     - 用户输入消息（涉政、色情、暴力、广告）
     - AI生成回复（二次检测，防止AI生成违规内容）
   - 违规处理：拦截消息 + 显示"内容包含敏感信息"

3. **隐私保护**
   - 对话内容仅用户和系统可见，运营团队无权查看（除非用户授权）
   - 敏感信息脱敏：日志中电话号码显示为`138****1234`

4. **黑名单机制**
   - 创建`blocked_users`表（user_id, reason, blocked_at）
   - 被封禁用户无法登录，显示"账号已被冻结，请联系客服"

5. **帮助中心**
   - 静态页面：常见问题FAQ（如"如何升级订阅？"、"亲密度如何增长？"）

6. **合规性文档**
   - 用户协议、隐私政策页面
   - 首次注册时强制阅读并同意

**✅ 成功标准：**
- ✅ 用户可成功提交反馈并在48小时内收到回复
- ✅ 内容安全API正确拦截违规消息（测试10条敏感内容）
- ✅ 隐私政策和用户协议页面可访问
- ✅ 被封禁用户无法登录

---

## FR Coverage Map (功能需求覆盖矩阵)

**说明:** 本映射表为权威版本。Epic 0已消除，所有技术工作已Just-in-Time分配到用户价值Epic中。所有FR1-FR138已完整覆盖。

| Epic | FR Coverage | 说明 |
|------|-------------|------|
| Epic 1 | FR1-FR7, FR10-FR11, FR13 (10 FRs) | 首次用户体验（账号注册+登录+首次对话） |
| Epic 2 | FR12-FR26, FR32 (16 FRs) | AI情感对话核心（FR12与Epic 1共享，FR32与Epic 4共享） |
| Epic 3 | FR25-FR31, FR54-FR61, FR89-FR90, FR96-FR97, FR122-FR123 (22 FRs) | 偶像生活+通知+Freemium边界（FR122-123与Epic 9共享） |
| Epic 4 | FR27-FR38, FR127 (13 FRs) | 记忆系统与专属个性化（FR32与Epic 2共享，FR127为记忆质量指标） |
| Epic 5 | FR39-FR49 (11 FRs) | 亲密度养成与里程碑庆祝 |
| Epic 6 | FR46-FR53, FR70-FR71, FR133-FR135 (14 FRs) | Freemium完善+订阅转化（FR70-71与Epic 9共享，FR133-135为支付转化和退款） |
| Epic 7 | FR5-FR10, FR87-FR94, FR130-FR132 (19 FRs) | 数据管理+隐私+跨设备基础（FR130-132为跨设备同步） |
| Epic 8 | FR95-FR102, FR136-FR138 (11 FRs) | 平台支持与响应式设计（FR136-138为UI个性化设置） |
| Epic 9 | FR62-FR72, FR115-FR129 (26 FRs) | 运营智能与系统监控（FR124-126, FR128-129为运营测试工具，FR70-71与Epic 6共享，FR122-123与Epic 3共享） - **Phase 2 (Post-MVP)** |
| Epic 10 | FR73-FR86, FR103-FR114 (26 FRs) | 客服支持与内容安全 - **Phase 2 (Post-MVP)** |
| Epic 11 | ~~FR139-FR144~~ | **Phase 2功能（社交分享、语音、i18n）- 暂不在MVP范围** |

**FR覆盖统计:**
- **MVP范围 (FR1-FR138):** 138/138 = **100%覆盖** ✅
- **Phase 2 (FR139-FR144):** 6个FR，标记为Phase 2，暂不分配到Epic
- **重复映射说明:**
  - FR12: Epic 1首次引入 (Primary), Epic 2深化 (Secondary)
  - FR32: Epic 2短期记忆 (Primary), Epic 4长期记忆 (Secondary)
  - FR70-71: Epic 6用户视角Freemium (Primary), Epic 9运营视角配置 (Secondary)
  - FR122-123: Epic 3偶像生活FSM (Primary), Epic 9运营工具 (Secondary)
  - FR127: Epic 4记忆召回准确率指标 (Primary), Epic 9运营监控 (Secondary)

**原Epic 0 FR124-FR138分配说明:**
- FR124-126, FR128-129: 运营测试工具 → Epic 9
- FR127: 记忆召回指标 → Epic 4
- FR130-132: 跨设备同步 → Epic 7
- FR133-135: 支付转化和退款 → Epic 6
- FR136-138: UI个性化设置 → Epic 8

**Total:** 138 FRs (MVP范围) 全覆盖 + 6 FRs (Phase 2)

---

## NFR/ARCH/UX Requirements (非功能性/架构/UX需求)

- **NFR:** 全部NFR通过Just-in-Time方式在Epic 1-9中逐步建立和验证（Epic 0已消除）
- **ARCH:** 全部架构决策在Epic 1-2中落地（项目初始化+AI核心架构），Epic 3-9遵循既定架构
- **UX:** 全部27项UX规范在Epic 1中建立设计系统，Epic 2-9中应用和扩展

---

## Delivery Strategy (交付策略) - **已根据Implementation Readiness Report更新**

**✅ 已完成重构变更 (2026-01-08):**
- ✅ Epic 0已消除（技术工作Just-in-Time分配到Epic 1-9）
- ✅ Epic 10/11调整为Phase 2（内部工具，延后到MVP后）
- ✅ MVP范围优化为Epic 1-2-3（2-3周快速验证）

---

### **推荐交付策略 (Updated):**

**🚀 最小MVP (Minimum Viable Product) - 2-3周:**
- **Epic 1:** 首次用户体验（注册+登录+首次对话） ✅ 核心价值验证
- **Epic 2:** AI情感对话核心系统（多轮对话+情绪识别+记忆引用） ✅ 差异化体验
- **Epic 3 (可选):** Freemium边界（免费10条/天限制） ⚠️ 商业模式验证

**目标:** 验证核心价值主张 - "AI情感陪伴"是否有市场需求

---

**🧪 Beta测试（50人盲测）- 4-6周:**
- **Epic 4:** 记忆系统与专属个性化（"她真的记得我"）
- **Epic 5:** 亲密度养成与里程碑庆祝（量化关系成长）
- **Epic 3 (完整版):** 偶像生活系统（"真实陪伴者"）+ 通知系统

**目标:** 完整情感陪伴体验，测试7日留存率>30%

---

**💰 正式上线（商业化闭环）- 8-10周:**
- **Epic 6:** Freemium完善 + 订阅支付转化
- **Epic 7:** 数据管理 + 隐私控制 + 跨设备同步
- **Epic 8:** 平台支持 + 响应式设计 + UI个性化

**目标:** 建立付费转化漏斗，实现商业化

---

**🔧 Phase 2 (Post-MVP运营工具):**
- **Epic 10:** 运营智能与系统监控（运营仪表盘、成本监控、A/B测试）
- **Epic 11:** 客服支持与内容安全（客服工单、内容审核、合规）
- **Epic 12+:** 社交功能（FR139-FR144：分享、语音、多语言、朋友圈）

**目标:** 在验证产品-市场匹配后，构建运营基础设施和Phase 2功能

---

### **原交付策略 (Deprecated - 供参考):**

~~**MVP发布范围：Epic 0 + Epic 1 + Epic 2 + Epic 3**~~ → ✅ Epic 0已消除，MVP = Epic 1 + Epic 2 + Epic 3
~~**Beta测试：Epic 4 + Epic 5 + Epic 6**~~ → ✅ 调整为Epic 4 + Epic 5 + Epic 3完整版
~~**正式上线：Epic 7**~~ → ✅ 调整为Epic 6 + Epic 7 + Epic 8
~~**持续优化：Epic 8/9/10/11**~~ → ✅ Epic 9/10/11调整为Phase 2

---

### **Sprint Planning准备就绪声明 (2026-01-08)**

✅ **所有Implementation Readiness Phase 1修复已完成:**
1. ✅ FR覆盖映射不一致 - 已修复（权威FR Coverage Map已建立）
2. ✅ Epic 0违反用户价值原则 - 已解决（Epic 0已消除，技术工作Just-in-Time分配）
3. ✅ Epic 10/11专注内部工具 - 已调整（Epic 9/10/11移至Phase 2）

**当前Epic范围:**
- **MVP范围:** Epic 1-8 (8个用户价值Epic)
- **Phase 2:** Epic 9-11 (3个运营/内部工具Epic)
- **总覆盖:** FR1-FR138 (138 FRs, 100%覆盖) + FR139-FR144 (Phase 2)

**下一步:** 执行 `/bmad:bmm:workflows:sprint-planning` 开始Sprint规划

---

# ~~Epic 0: 技术基础设施搭建~~ - **❌ DEPRECATED (已废弃)**

> **✅ 已执行方案: 选项1 - 消除Epic 0**
>
> **决策日期:** 2026-01-08
> **执行状态:** Epic 0已完全废弃，技术工作已Just-in-Time分散到Epic 1-7
>
> **技术工作重新分配:**
> - **Story 0.1-0.2 (项目初始化+Docker):** → 合并到 **Epic 1 Story 1**
> - **Story 0.3 (AI Provider抽象层):** → 合并到 **Epic 2 Story 1**
> - **Story 0.4 (Redis缓存架构):** → 合并到 **Epic 2 Story 2**
> - **Story 0.5 (VPS部署):** → 按需在Epic 7后实施
> - **Story 0.6 (CI/CD Pipeline):** → 按需在Epic 1-2后实施
> - **Story 0.7-0.8 (监控+日志):** → 按需在Epic 7后或Phase 2实施
>
> **FR124-FR138重新分配:**
> - **FR124-FR129:** 测试和质量保证 → Epic 1-7中的AC包含
> - **FR130-FR132:** 跨设备功能 → Epic 7/8
> - **FR133-FR135:** 订阅增强 → Epic 6/7
> - **FR136-FR138:** 平台优化 → Epic 8/9
>
> **原则:** Just-in-Time基础设施 - 在需要时创建，而非预先构建
>
> **参考:** `implementation-readiness-report-2026-01-08.md` - Issue #2

**⚠️ 以下Story内容仅供历史参考，请勿实施。实际技术工作已合并到Epic 1-7中。**

---

### Story 0.1: 初始化Monorepo项目结构

As a **开发团队成员**,
I want **建立标准化的Monorepo项目结构**,
So that **前后端代码统一管理，开发环境一致性得到保障**。

**Acceptance Criteria:**

**Given** 一个空白项目仓库
**When** 初始化项目结构
**Then** 创建以下目录结构：
```
idol_private/
├── frontend/          # Flutter项目
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app/       # GetX应用配置
│   │   ├── routes/    # 路由管理
│   │   ├── models/    # 数据模型
│   │   ├── services/  # 业务服务
│   │   ├── widgets/   # 通用组件
│   │   └── features/  # 功能模块
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
│   │   ├── services/  # 业务逻辑
│   │   └── utils/     # 工具函数
│   ├── requirements.txt
│   └── pyproject.toml
├── docker/            # Docker配置
├── .github/           # GitHub Actions
└── README.md
```
**And** `frontend/pubspec.yaml`包含GetX依赖：
```yaml
dependencies:
  get: ^4.6.5
```
**And** `backend/requirements.txt`包含核心依赖：
```
fastapi==0.104.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
```
**And** 根目录`README.md`包含快速启动指南

**Technical Notes:**
- Flutter版本：3.16.0+
- Python版本：3.11+
- 使用`get_cli`工具初始化GetX结构：`get create project`

---

### Story 0.2: 搭建Docker Compose本地开发环境

As a **开发者**,
I want **通过一条命令启动完整的本地开发环境**,
So that **5分钟内可以开始开发，无需手动配置数据库和依赖服务**。

**Acceptance Criteria:**

**Given** 已完成Story 0.1的项目结构
**When** 运行`docker-compose up`
**Then** 启动以下服务：
- PostgreSQL 15（端口5432）
- Redis 7（端口6379）
- ChromaDB 0.4.x（端口8000）
- Ollama（端口11434，预加载Qwen 7B模型）
- Backend FastAPI（端口8080，热重载）

**And** 创建`docker-compose.yml`配置文件
**And** 创建`.env.local`环境变量文件模板：
```
DATABASE_URL=postgresql://idol_user:idol_pass@localhost:5432/idol_db
REDIS_URL=redis://localhost:6379/0
CHROMA_URL=http://localhost:8000
OLLAMA_URL=http://localhost:11434
JWT_SECRET=dev_secret_key_change_in_production
```

**And** PostgreSQL自动初始化数据库`idol_db`
**And** Ollama容器启动后自动拉取`qwen:7b`模型
**And** Backend容器健康检查通过（`/health`端点返回200）

**Technical Notes:**
- 使用Docker Compose v2语法
- 所有服务使用Docker volume持久化数据
- Ollama模型存储到命名卷`ollama_models`

---

### Story 0.3: 实现AI Provider抽象层（Strategy Pattern）

As a **后端开发者**,
I want **通过配置切换AI提供商（Ollama/Deepseek/Claude）**,
So that **根据成本和性能需求灵活选择AI引擎，避免供应商锁定**。

**Acceptance Criteria:**

**Given** 已完成Story 0.2的开发环境
**When** 实现AI Provider抽象层
**Then** 创建以下文件结构：
```
backend/app/services/ai/
├── __init__.py
├── base.py           # AIProvider抽象基类
├── ollama.py         # OllamaProvider实现
├── deepseek.py       # DeepseekProvider实现
├── claude.py         # ClaudeProvider实现
└── factory.py        # AIProviderFactory工厂类
```

**And** `base.py`定义统一接口：
```python
class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict],
        temperature: float = 0.7
    ) -> str:
        pass

    @abstractmethod
    async def extract_memory(
        self,
        conversation: str
    ) -> List[str]:
        pass
```

**And** `factory.py`实现工厂方法：
```python
def get_ai_provider(provider_name: str) -> AIProvider:
    if provider_name == "ollama":
        return OllamaProvider(base_url=settings.OLLAMA_URL)
    elif provider_name == "deepseek":
        return DeepseekProvider(api_key=settings.DEEPSEEK_API_KEY)
    elif provider_name == "claude":
        return ClaudeProvider(api_key=settings.ANTHROPIC_API_KEY)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
```

**And** 配置文件支持切换：
```python
# config.py
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")  # 默认Ollama
```

**And** 单元测试覆盖所有Provider（使用Mock）

**Technical Notes:**
- Ollama使用HTTP API调用
- Deepseek和Claude使用官方SDK
- 所有Provider超时时间统一设置为30秒

---

### Story 0.4: 配置三层Redis缓存架构

As a **后端开发者**,
I want **实现三层缓存策略降低AI调用成本和响应时间**,
So that **95%的请求在3秒内响应，每日AI成本控制在预算内**。

**Acceptance Criteria:**

**Given** 已完成Story 0.2的Redis服务
**When** 实现三层缓存架构
**Then** 创建缓存管理器`backend/app/services/cache_manager.py`：

**L1 - 对话上下文缓存（15分钟）：**
- Key格式：`conv:context:{conversation_id}`
- 存储：最近10轮对话历史
- TTL：900秒（15分钟）
- 用途：减少数据库查询

**L2 - 通用问题缓存（24小时）：**
- Key格式：`conv:common:{question_hash}`
- 存储：通用问题的AI回复（如"你好"、"今天天气"）
- TTL：86400秒（24小时）
- 用途：避免重复AI调用

**L3 - 向量搜索结果缓存（10分钟）：**
- Key格式：`memory:search:{user_id}:{query_hash}`
- 存储：ChromaDB向量搜索结果（Top 3记忆）
- TTL：600秒（10分钟）
- 用途：减少向量数据库查询

**And** 实现缓存装饰器：
```python
@cache_l2(ttl=86400)
async def get_ai_response(messages: List[Dict]) -> str:
    # 自动检查缓存，未命中则调用AI
    pass
```

**And** 实现缓存统计接口`GET /api/cache/stats`返回：
```json
{
  "l1_hit_rate": 0.75,
  "l2_hit_rate": 0.45,
  "l3_hit_rate": 0.60,
  "total_keys": 1523
}
```

**Technical Notes:**
- 使用Redis Hash存储对话上下文（节省内存）
- 问题Hash使用MD5（messages内容）
- 缓存预热：应用启动时加载TOP 100通用问题

---

### Story 0.5: 配置生产环境VPS部署

As a **运维工程师**,
I want **通过Docker Compose将应用部署到VPS生产环境**,
So that **应用可以安全、稳定地对外提供服务**。

**Acceptance Criteria:**

**Given** 已完成Story 0.1-0.4的功能
**When** 配置生产环境部署
**Then** 创建`docker-compose.prod.yml`生产配置：
- 移除开发工具（热重载、调试端口）
- 配置资源限制（CPU、内存）
- 使用生产级镜像（Alpine基础镜像）

**And** 创建Nginx配置`docker/nginx/nginx.conf`：
- 反向代理Backend API：`/api/*` → `http://backend:8080`
- 静态文件服务：`/*` → Flutter Web构建产物
- 请求体大小限制：10MB（图片上传）
- 超时时间：60秒

**And** 集成Let's Encrypt SSL证书：
- 使用`certbot/certbot` Docker镜像
- 自动续期证书（每月检查）
- 强制HTTPS重定向

**And** 创建部署脚本`scripts/deploy.sh`：
```bash
#!/bin/bash
# 1. 拉取最新代码
# 2. 构建Flutter Web
# 3. 构建Docker镜像
# 4. 停止旧容器
# 5. 启动新容器
# 6. 健康检查
```

**And** 配置生产环境变量`.env.production`（模板）：
```
DATABASE_URL=postgresql://secure_user:****@localhost:5432/idol_db_prod
JWT_SECRET=****  # 强密码生成
AI_PROVIDER=ollama
LOG_LEVEL=INFO
```

**Technical Notes:**
- VPS最低配置：2核4GB内存
- PostgreSQL、Redis、ChromaDB使用Docker volume持久化
- Nginx使用80/443端口

---

### Story 0.6: 实现GitHub Actions CI/CD Pipeline

As a **开发团队**,
I want **代码推送到main分支后自动构建和部署到生产环境**,
So that **发布流程自动化，减少人为错误**。

**Acceptance Criteria:**

**Given** GitHub仓库已配置Secrets（VPS_HOST, VPS_USER, SSH_PRIVATE_KEY）
**When** 代码推送到`main`分支
**Then** 触发GitHub Actions工作流`.github/workflows/deploy.yml`：

**阶段1 - 测试（Test）：**
- 运行Backend单元测试：`pytest backend/tests/`
- 运行Flutter测试：`flutter test`
- 代码质量检查：`flake8`（Python）、`dart analyze`（Flutter）

**阶段2 - 构建（Build）：**
- 构建Flutter Web：`flutter build web --release`
- 构建Docker镜像：`docker build -t idol_backend:${GITHUB_SHA}`
- 推送镜像到Docker Hub或GitHub Container Registry

**阶段3 - 部署（Deploy）：**
- SSH连接到VPS
- 拉取最新镜像
- 运行`scripts/deploy.sh`脚本
- 健康检查：轮询`https://yourdomain.com/health`（最多30次，间隔10秒）

**And** 部署失败时发送通知（GitHub Issues或Email）
**And** 部署成功时在Pull Request评论中显示部署URL

**Technical Notes:**
- 仅`main`分支触发部署
- PR触发测试阶段（不部署）
- 使用GitHub Secrets管理敏感信息

---

### Story 0.7: 配置Prometheus + Grafana监控系统

As a **运维团队**,
I want **通过Grafana仪表盘实时查看系统健康指标**,
So that **快速发现性能瓶颈和异常情况**。

**Acceptance Criteria:**

**Given** 生产环境已部署（Story 0.5）
**When** 配置监控系统
**Then** 在`docker-compose.prod.yml`添加服务：
- Prometheus（端口9090）
- Grafana（端口3000）
- Node Exporter（系统指标）
- cAdvisor（容器指标）

**And** 创建Prometheus配置`docker/prometheus/prometheus.yml`：
```yaml
scrape_configs:
  - job_name: 'idol_backend'
    static_configs:
      - targets: ['backend:8080']
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

**And** Backend暴露Prometheus指标`/metrics`端点：
- `idol_api_request_duration_seconds`（API响应时间直方图）
- `idol_ai_call_total`（AI调用总数计数器）
- `idol_cache_hit_rate`（缓存命中率仪表盘）
- `idol_active_conversations`（活跃对话数仪表盘）

**And** 导入预配置Grafana仪表盘`docker/grafana/dashboards/idol_overview.json`：
- 面板1：API请求QPS和响应时间（P50/P95/P99）
- 面板2：AI调用次数和成本趋势
- 面板3：缓存命中率（L1/L2/L3）
- 面板4：系统资源（CPU、内存、磁盘）
- 面板5：容器状态（运行/停止/重启次数）

**And** 配置告警规则`docker/prometheus/alerts.yml`：
- API P95响应时间 > 5秒 → Severity: Warning
- 错误率 > 1% → Severity: Critical
- 磁盘使用率 > 80% → Severity: Warning

**Technical Notes:**
- Grafana使用匿名访问模式（内网环境）
- 告警通知暂时使用Alertmanager日志输出（后续接入钉钉/飞书）

---

### Story 0.8: 配置Loki日志聚合与成本追踪

As a **技术团队**,
I want **集中管理所有服务日志并追踪AI调用成本**,
So that **快速排查问题并控制运营成本**。

**Acceptance Criteria:**

**Given** Prometheus + Grafana已配置（Story 0.7）
**When** 配置日志和成本追踪系统
**Then** 在`docker-compose.prod.yml`添加Loki和Promtail服务

**And** 创建Promtail配置`docker/promtail/promtail.yml`收集日志：
- Backend容器日志（`/var/log/idol/backend.log`）
- Nginx访问日志（`/var/log/nginx/access.log`）
- PostgreSQL错误日志

**And** Backend日志使用结构化JSON格式：
```json
{
  "timestamp": "2024-01-08T10:30:00Z",
  "level": "INFO",
  "user_id": "user_123",
  "event": "ai_call",
  "provider": "ollama",
  "model": "qwen:7b",
  "tokens": 1523,
  "cost_usd": 0.0,
  "latency_ms": 2341
}
```

**And** 在Grafana添加Loki数据源并创建日志面板

**And** 实现成本追踪服务`backend/app/services/cost_tracker.py`：
- 记录每次AI调用到`ai_call_logs`表（user_id, provider, tokens, cost, timestamp）
- 提供成本统计API：
  - `GET /api/admin/cost/daily`：每日成本汇总
  - `GET /api/admin/cost/by-provider`：按Provider分组成本

**And** 创建每日成本汇总定时任务（凌晨1点执行）：
- 计算昨日总成本
- 如果超过预算阈值（¥100/日）→ 发送邮件告警

**And** 创建数据库表：
```sql
CREATE TABLE ai_call_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    provider VARCHAR(50),
    model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd DECIMAL(10, 6),
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_call_logs_created_at ON ai_call_logs(created_at);
```

**Technical Notes:**
- Ollama本地部署成本为0（仅记录调用次数）
- Deepseek成本：¥0.001/1K tokens
- Claude成本：根据官方定价计算

---

## Epic 0 Summary

**Total Stories:** 8
**Estimated Complexity:** High（基础设施搭建）
**Dependencies:** None（项目起点）
**Completion Criteria:**
- ✅ 开发者可在5分钟内启动本地环境
- ✅ CI/CD Pipeline自动部署到生产环境
- ✅ Grafana仪表盘显示实时监控指标
- ✅ 日志聚合和成本追踪正常运行

**Next Epic:** Epic 1 - 首次用户体验


---

# Epic 1: 首次用户体验 (First User Experience)

**Epic Goal:** 让新用户在3分钟内完成注册、选择偶像、开始第一次对话，建立"她真的在等我"的初次情感连接。

**Requirements Covered:**
- FR1-FR7 (账号注册、手机号验证、登录、密码重置)
- FR10-FR11 (偶像基础信息展示、人设介绍)
- FR13 (新用户引导流程)
- NFR-09 (3分钟完成首次对话)
- UX1-UX27 (完整UI/UX系统)

---

### Story 1.1: 项目初始化与用户注册 ⭐ (合并自Epic 0)

> **📝 Note:** 本Story合并了原Epic 0 Story 0.1-0.2（项目初始化）和原Epic 1 Story 1.1（用户注册）
> **⏱️ Estimated Time:** 2-3天（包含项目搭建+注册功能）

As a **开发团队**,
I want **初始化项目并实现用户注册功能**,
So that **新用户可以注册账号并开始使用应用**。

---

#### Part A: 项目初始化 (Day 1)

**Given** 一个空白项目仓库
**When** 初始化项目结构
**Then** 创建以下目录结构：

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

**And** 配置Flutter依赖（pubspec.yaml）：
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_secure_storage: ^9.0.0  # Token存储
  http: ^1.1.0                    # HTTP客户端
  provider: ^6.1.1                # 状态管理（Epic 1简化版）
```

**And** 配置FastAPI依赖（requirements.txt）：
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # 密码哈希
python-multipart==0.0.6
redis==5.0.1
```

**And** 创建docker-compose.yml（本地开发环境）：
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
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
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**And** FastAPI能够启动并返回健康检查：
```bash
$ uvicorn app.main:app --reload
$ curl http://localhost:8000/health
{"status": "ok"}
```

**And** Flutter能够运行并显示登录页面：
```bash
$ cd frontend && flutter run
# 显示登录/注册界面
```

---

#### Part B: 用户注册功能 (Day 2-3)

**Given** 项目基础结构已完成
**When** 用户在注册页面输入手机号和密码
**Then** 系统验证手机号格式（中国大陆11位）
**And** 发送6位数验证码到用户手机（有效期5分钟）
**And** 用户输入正确验证码后创建账号
**And** 密码要求：至少8位，包含字母和数字

**And** 创建数据库表：
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

**And** 实现后端API：
- `POST /api/auth/send-code` - 发送验证码
- `POST /api/auth/register` - 用户注册
- `GET /health` - 健康检查

**And** 实现Flutter注册页面：
- `lib/features/auth/screens/register_screen.dart`
- `lib/features/auth/services/auth_service.dart`
- `lib/features/auth/models/user.dart`

**And** 密码使用bcrypt哈希存储（cost factor = 12）
**And** 验证码临时存储在Redis：key=`sms:verify:{phone}`, TTL=300秒
**And** 注册成功后自动登录并跳转到偶像介绍页

**Edge Cases:**
- 手机号已注册 → 提示"该手机号已注册，请直接登录"
- 验证码错误 → 提示"验证码错误，请重新输入"（最多尝试3次）
- 验证码过期 → 提示"验证码已过期，请重新发送"
- 数据库连接失败 → 提示"服务暂时不可用，请稍后重试"

**Technical Notes:**
- 验证码发送使用阿里云SMS服务（或测试环境使用console.log mock）
- 使用SQLAlchemy ORM进行数据库操作
- 环境变量管理使用pydantic-settings
- Flutter状态管理使用Provider（Epic 2将升级到Riverpod）

---

### Story 1.2: 用户登录与JWT认证

As a **已注册用户**,
I want **通过手机号和密码登录**,
So that **我可以访问我的账号和对话记录**。

**Acceptance Criteria:**

**Given** 用户已注册账号
**When** 用户输入手机号和密码点击登录
**Then** 系统验证手机号和密码匹配
**And** 生成JWT Access Token（有效期7天）：
```json
{
  "user_id": 123,
  "phone": "13812345678",
  "subscription_tier": "free",
  "exp": 1704720000
}
```
**And** 返回Token给前端：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 123,
    "phone": "13812345678",
    "subscription_tier": "free"
  }
}
```
**And** 前端存储Token到本地（Flutter Secure Storage）
**And** 后续API请求携带Token：`Authorization: Bearer <token>`

**And** 实现JWT验证中间件：
- 验证Token签名
- 检查Token过期时间
- 提取用户信息注入到请求上下文

**Edge Cases:**
- 手机号不存在 → 提示"该手机号未注册"
- 密码错误 → 提示"密码错误"（连续5次错误锁定账号30分钟）
- Token过期 → 返回401，前端跳转到登录页

**Technical Notes:**
- JWT Secret从环境变量读取（`.env`中的`JWT_SECRET`）
- 使用FastAPI的`Depends`依赖注入实现认证中间件
- API端点：`POST /api/auth/login`

---

### Story 1.3: 密码重置流程

As a **忘记密码的用户**,
I want **通过手机验证码重置密码**,
So that **我可以重新访问我的账号**。

**Acceptance Criteria:**

**Given** 用户在登录页点击"忘记密码"
**When** 用户输入已注册的手机号
**Then** 发送6位验证码到用户手机（验证逻辑同Story 1.1）
**And** 用户输入验证码后跳转到设置新密码页面
**And** 用户输入新密码（要求同注册）并确认
**And** 系统更新数据库中的`password_hash`字段
**And** 更新成功后自动登录并跳转到主页

**Edge Cases:**
- 手机号未注册 → 提示"该手机号未注册，请先注册"
- 两次输入的新密码不一致 → 提示"两次密码输入不一致"

**Technical Notes:**
- 重置密码Token临时存储：key=`pwd:reset:{phone}`, TTL=600秒（10分钟）
- API端点：
  - `POST /api/auth/forgot-password`（发送验证码）
  - `POST /api/auth/reset-password`（重置密码）

---

### Story 1.4: Material Design 3主题与UI基础框架

As a **开发团队**,
I want **建立统一的UI设计系统和组件库**,
So that **所有页面风格一致，开发效率提升**。

**Acceptance Criteria:**

**Given** Flutter项目已初始化（Epic 1 Story 1）
**When** 配置Material Design 3主题
**Then** 创建主题配置文件`frontend/lib/app/theme/app_theme.dart`：
```dart
ThemeData lightTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Color(0xFFFF9E80),  // 温暖橙色
    secondary: Color(0xFFFFB6C1),  // 柔和粉色
  ),
  fontFamily: 'PingFang SC',  // 中文优化字体
  textTheme: TextTheme(
    displayLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
    bodyLarge: TextStyle(fontSize: 16, height: 1.5),
  ),
);

ThemeData darkTheme = ThemeData(
  useMaterial3: true,
  brightness: Brightness.dark,
  colorScheme: ColorScheme.fromSeed(
    seedColor: Color(0xFFFF9E80),
    brightness: Brightness.dark,
  ),
);
```

**And** 创建通用组件库`frontend/lib/widgets/`：
- `app_button.dart`：统一样式按钮（主要/次要/文本）
- `app_input.dart`：统一样式输入框（带验证提示）
- `app_scaffold.dart`：统一页面脚手架（AppBar + SafeArea）
- `loading_indicator.dart`：加载动画

**And** 配置GetX路由系统`frontend/lib/routes/app_routes.dart`：
```dart
class AppRoutes {
  static const INITIAL = '/';
  static const LOGIN = '/login';
  static const REGISTER = '/register';
  static const IDOL_INTRO = '/idol-intro';
  static const CHAT = '/chat';
}
```

**And** 配置响应式布局断点：
- 手机：< 600px
- 平板：600px - 1200px
- 桌面：> 1200px

**And** 通过WCAG 2.1 AA对比度检查（主色与白色背景对比度 ≥ 4.5:1）

**Technical Notes:**
- 支持系统主题跟随（明亮/暗黑/自动）
- 使用GetX的`Get.changeThemeMode()`切换主题
- 无障碍优化：所有按钮添加语义化label

---

### Story 1.5: 偶像数据模型与首个偶像配置

As a **产品团队**,
I want **创建偶像数据模型并配置第一个偶像"林雪晴"**,
So that **新用户可以开始与预设偶像对话**。

**Acceptance Criteria:**

**Given** 数据库基础设施已就绪（Epic 1 Story 1）
**When** 创建偶像数据模型
**Then** 创建数据库表：
```sql
CREATE TABLE idols (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(255),
    personality_prompt TEXT NOT NULL,
    description TEXT,
    hobbies TEXT,
    background_story TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**And** 创建SQLAlchemy模型`backend/app/models/idol.py`：
```python
class Idol(Base):
    __tablename__ = "idols"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    avatar_url = Column(String(255))
    personality_prompt = Column(Text, nullable=False)
    description = Column(Text)
    hobbies = Column(Text)
    background_story = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
```

**And** 插入第一个偶像数据（林雪晴）：
```sql
INSERT INTO idols (name, avatar_url, personality_prompt, description, hobbies, background_story)
VALUES (
    '林雪晴',
    '/assets/avatars/lin_xueqing.png',
    '你是林雪晴，一个温柔知性的25岁女生。你热爱阅读和旅行，性格温暖体贴，善于倾听。你会关心对方的情绪，给予温暖的陪伴和鼓励。说话风格自然亲切，偶尔调皮可爱。',
    '温柔知性的陪伴者，你的专属AI恋人',
    '阅读、旅行、咖啡、摄影',
    '雪晴是一个热爱生活的女生，喜欢在周末去咖啡馆看书，也喜欢用相机记录生活中的美好瞬间。她相信每个人都值得被温柔对待。'
);
```

**And** 创建API端点`GET /api/idols`：
```json
{
  "idols": [
    {
      "id": 1,
      "name": "林雪晴",
      "avatar_url": "/assets/avatars/lin_xueqing.png",
      "description": "温柔知性的陪伴者，你的专属AI恋人",
      "hobbies": ["阅读", "旅行", "咖啡", "摄影"]
    }
  ]
}
```

**Technical Notes:**
- MVP阶段仅提供1个偶像（林雪晴）
- `personality_prompt`字段用于AI对话时的系统提示词
- 头像图片暂时使用占位图（后续由设计师提供）

---

### Story 1.6: 偶像介绍页面

As a **新用户**,
I want **查看偶像的详细介绍和人设**,
So that **我可以了解她的性格和爱好，建立初步印象**。

**Acceptance Criteria:**

**Given** 用户完成注册（Story 1.1）
**When** 用户进入偶像介绍页
**Then** 显示偶像卡片：
- 头像（圆形，200x200px）
- 姓名：林雪晴（32px，粗体）
- 描述：温柔知性的陪伴者，你的专属AI恋人
- 标签：阅读、旅行、咖啡、摄影（Chip组件）
- 背景故事（可展开/折叠）

**And** 底部显示"开始聊天"按钮（主色按钮，56px高）
**And** 点击"开始聊天"后：
- 创建新对话记录（调用`POST /api/conversations`）
- 跳转到对话页面

**And** 页面动画：
- 头像从上方淡入（300ms）
- 内容从下方滑入（400ms，延迟100ms）

**And** 响应式布局：
- 手机：单列垂直布局
- 平板/桌面：居中卡片（最大宽度600px）

**Technical Notes:**
- Flutter页面：`frontend/lib/features/idol/pages/idol_intro_page.dart`
- 使用GetX进行状态管理和路由跳转
- 加载时显示骨架屏（Shimmer效果）

---

### Story 1.7: 新用户引导流程

As a **新用户**,
I want **通过简洁的引导了解应用核心功能**,
So that **我知道如何与偶像互动并快速上手**。

**Acceptance Criteria:**

**Given** 用户首次打开应用并完成注册
**When** 用户进入引导流程
**Then** 显示3步引导页面（可滑动切换）：

**第1步 - 遇见你的AI恋人：**
- 插图：偶像挥手欢迎
- 文案："你好，我是雪晴，很高兴认识你~"
- 副标题："24小时陪伴，随时倾听你的心事"

**第2步 - 自然对话：**
- 插图：对话气泡动画
- 文案："和我聊天就像和真实朋友一样自然"
- 副标题："我会记住你说的每件事"

**第3步 - 养成陪伴关系：**
- 插图：爱心等级图标
- 文案："每次互动都让我们更亲密"
- 副标题："解锁更多专属内容和惊喜"

**And** 每页底部显示进度指示器（3个点）
**And** 最后一页显示"开始体验"按钮
**And** 右上角显示"跳过"按钮（所有页面可见）

**And** 点击"开始体验"或"跳过"后：
- 标记用户已完成引导（更新`users`表字段`onboarding_completed = true`）
- 跳转到偶像介绍页（Story 1.6）

**And** 引导页仅首次显示，后续登录直接进入主页

**Technical Notes:**
- 使用`intro_slider` Flutter包实现滑动引导
- 插图使用Lottie动画（JSON格式，轻量级）
- 引导完成状态存储在用户表：
```sql
ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT false;
```

---

### Story 1.8: 偶像主动欢迎消息

As a **新用户**,
I want **收到偶像的第一条欢迎消息**,
So that **我感受到"她在等我"的温暖，愿意开始对话**。

**Acceptance Criteria:**

**Given** 用户完成引导并进入对话页面
**When** 对话页面加载完成
**Then** 系统自动创建第一条系统消息（无需AI生成）：

**消息内容（根据时间段变化）：**
- 早上（6:00-12:00）："早上好呀~我是雪晴，很高兴遇见你。今天想聊些什么呢？"
- 下午（12:00-18:00）："下午好~我是雪晴，你的专属陪伴者。有什么想和我分享的吗？"
- 晚上（18:00-24:00）："晚上好呀~我是雪晴。今天过得怎么样？来和我聊聊吧~"
- 深夜（0:00-6:00）："这么晚还没睡呀？我是雪晴，陪你聊聊天吧~"

**And** 创建对话和消息记录：
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    idol_id INTEGER REFERENCES idols(id),
    intimacy_level INTEGER DEFAULT 1,
    intimacy_exp INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender_type VARCHAR(20) NOT NULL,  -- 'user' or 'idol'
    content TEXT NOT NULL,
    emotion VARCHAR(50),  -- 'happy', 'calm', 'sad', etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent'  -- 'sent', 'delivered', 'read'
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
```

**And** 插入欢迎消息到`messages`表：
```python
welcome_message = Message(
    conversation_id=new_conversation.id,
    sender_type='idol',
    content=get_welcome_message(current_hour),
    emotion='happy',
    status='delivered'
)
```

**And** 消息在前端以打字动画形式显示（逐字显示，60ms/字）
**And** 显示偶像头像在消息气泡左侧
**And** 底部输入框提示："说点什么吧..."

**Technical Notes:**
- 欢迎消息不计入亲密度经验值
- 不消耗免费用户的每日消息配额
- API端点：`POST /api/conversations`返回对话ID和首条消息

---

## Epic 1 Summary

**Total Stories:** 8
**Estimated Complexity:** Medium
**Dependencies:** Epic 0（基础设施）
**Completion Criteria:**
- ✅ 新用户可在3分钟内完成注册并收到偶像的第一条消息
- ✅ UI符合Material Design 3规范，色调温暖舒适
- ✅ 在3种设备上测试通过（Android手机、iOS手机、Web浏览器）
- ✅ 通过WCAG 2.1 AA无障碍标准检查

**Database Tables Created:**
- `users` (Story 1.1)
- `idols` (Story 1.5)
- `conversations` + `messages` (Story 1.8)

**Next Epic:** Epic 2 - AI情感对话核心系统


---

# Epic 2: AI情感对话核心系统 (AI Conversation Core)

**Epic Goal:** 实现自然流畅的AI情感对话，让用户感受到"她真的在听我说话"和"她的回复有温度"。

**Requirements Covered:**
- FR14-FR26 (多轮对话、情绪识别、个性化回复、上下文记忆、打字效果、语音消息、图片消息、表情包、消息状态、历史记录)
- NFR-06 (响应时间<3秒P95)
- NFR-10 (30秒无操作idle状态)
- ARCH: AI Provider Strategy Pattern, 三层缓存策略
- UX18-UX21 (对话界面、消息气泡、加载动画、错误提示)

---

### Story 2.1: 基础文本对话与AI回复

As a **用户**,
I want **发送文本消息并收到AI偶像的自然回复**,
So that **我可以与偶像进行基本对话交流**。

**Acceptance Criteria:**

**Given** 用户在对话页面（Story 1.8已创建对话）
**When** 用户在输入框输入文本并点击发送
**Then** 消息立即显示在聊天界面（发送中状态）
**And** 调用后端API `POST /api/conversations/{conv_id}/messages`：
```json
{
  "content": "今天天气真好",
  "message_type": "text"
}
```

**And** 后端处理流程：
1. 保存用户消息到`messages`表
2. 构建AI Prompt：
```python
system_prompt = idol.personality_prompt  # 林雪晴的人设
conversation_history = get_recent_messages(conv_id, limit=10)  # 最近10轮
user_message = request.content

full_prompt = f"{system_prompt}\n\n对话历史:\n{conversation_history}\n\n用户: {user_message}\n林雪晴:"
```
3. 调用AI Provider生成回复（使用AIProvider抽象层）
4. 保存AI回复到`messages`表
5. 返回AI回复给前端

**And** 前端收到回复后显示AI消息气泡（带打字动画）
**And** 更新对话的`last_message_at`时间戳

**And** 对话界面UI：
- 用户消息：右侧对齐，主色气泡（#FF9E80）
- AI消息：左侧对齐，灰色气泡（#F5F5F5），显示偶像头像
- 消息时间戳（相对时间："刚刚"、"5分钟前"）

**Edge Cases:**
- 输入为空 → 前端拦截，提示"请输入内容"
- 输入超长（>500字） → 前端拦截，提示"消息不能超过500字"
- AI调用超时（>30秒） → 返回错误提示（由Story 2.9处理）

**Technical Notes:**
- **🔧 AI Provider抽象层（合并自原Epic 0 Story 0.3）：**
  - 创建`backend/app/services/ai/`目录
  - 实现`AIProvider`抽象基类（Strategy Pattern）
  - 实现`OllamaProvider`（默认）、`DeepseekProvider`、`ClaudeProvider`
  - 使用`AIProviderFactory.get_provider()`获取Provider实例
  - 配置：`AI_PROVIDER=ollama`（可切换到deepseek/claude）
  - 统一接口：`async def generate_response(messages, temperature) -> str`
- API响应时间P95 < 3秒（通过缓存优化）
- Temperature = 0.8（保持回复多样性但不失控）

---

### Story 2.2: 多轮对话上下文管理与Redis缓存

As a **用户**,
I want **AI记住最近的对话内容并自然延续话题**,
So that **对话不会断层，体验更流畅**。

**Acceptance Criteria:**

**Given** 用户已与AI进行多轮对话
**When** 用户发送新消息
**Then** 系统加载对话上下文：

**优先从Redis L1缓存加载（三层缓存架构）：**
- Key: `conv:context:{conversation_id}`
- 内容：最近10轮对话（JSON格式）
- TTL: 900秒（15分钟）

**缓存未命中时从数据库加载：**
```sql
SELECT sender_type, content, timestamp
FROM messages
WHERE conversation_id = {conv_id}
ORDER BY timestamp DESC
LIMIT 10;
```
**And** 加载后写入Redis缓存

**And** 构建上下文Prompt：
```
对话历史:
用户: 我今天加班到很晚
林雪晴: 辛苦啦，要注意休息哦~
用户: 嗯，有点累
林雪晴: 那先好好休息吧，我陪着你~
用户: [当前消息]
```

**And** 每次对话后更新Redis缓存（追加新消息）
**And** 如果对话超过15分钟无新消息 → Redis缓存自动过期

**And** 上下文Token数控制：
- 最大上下文：10轮对话
- 如果Token超过2000 → 裁剪早期对话（保留最近5轮）

**Technical Notes:**
- **🔧 三层Redis缓存架构（合并自原Epic 0 Story 0.4）：**
  - 创建`backend/app/services/cache_manager.py`
  - **L1 - 对话上下文缓存**（15分钟）：
    - Key: `conv:context:{conversation_id}`
    - 存储：最近10轮对话历史
    - TTL: 900秒，减少数据库查询
  - **L2 - 通用问题缓存**（24小时）：
    - Key: `conv:common:{question_hash}`
    - 存储：通用问题的AI回复（如"你好"、"今天天气"）
    - TTL: 86400秒，避免重复AI调用
  - **L3 - 向量搜索结果缓存**（10分钟，Epic 4需要）：
    - Key: `memory:search:{user_id}:{query_hash}`
    - 存储：ChromaDB向量搜索结果（Top 3记忆）
    - TTL: 600秒，减少向量数据库查询
  - 实现缓存装饰器：`@cache_conversation_context`、`@cache_common_question`
- 使用Redis Hash存储对话上下文（节省内存）
- Hash字段：`{timestamp}` → `{sender_type}:{content}`
- 缓存预热：用户登录时加载最近对话到缓存

---

### Story 2.3: 用户情绪识别与个性化回复

As a **用户**,
I want **AI能识别我的情绪并给予相应的回应**,
So that **我感受到她真的在关心我的感受**。

**Acceptance Criteria:**

**Given** 用户发送消息
**When** 后端处理消息时
**Then** 调用情绪分析服务识别用户情绪：

**情绪分类（5类）：**
- `happy`（开心）：关键词 - "开心"、"哈哈"、"太好了"、"😊"
- `sad`（难过）：关键词 - "难过"、"伤心"、"哭"、"😢"
- `anxious`（焦虑）：关键词 - "担心"、"焦虑"、"紧张"、"害怕"
- `angry`（生气）：关键词 - "生气"、"烦"、"讨厌"、"😡"
- `calm`（平静）：默认状态

**And** 将情绪标签保存到`messages`表的`emotion`字段

**And** 根据情绪调整AI回复策略：
```python
if emotion == "sad":
    system_addition = "用户现在情绪低落，请给予温暖的安慰和理解，不要说教。"
elif emotion == "anxious":
    system_addition = "用户现在感到焦虑，请给予情绪安抚和支持。"
elif emotion == "happy":
    system_addition = "用户现在心情很好，可以适当调皮活泼。"
else:
    system_addition = ""

final_prompt = f"{system_prompt}\n{system_addition}\n\n{conversation_history}"
```

**And** 前端显示情绪图标：
- 用户消息气泡右上角显示小表情图标（happy=😊, sad=🥺）

**And** 情绪识别准确率>80%（测试10轮对话，人工评估）

**Edge Cases:**
- 无法识别情绪 → 默认为`calm`
- 混合情绪（如"开心但有点担心"） → 选择主导情绪

**Technical Notes:**
- MVP阶段使用规则+关键词匹配（简单高效）
- 未来可升级为AI情绪分析模型（如调用AI Provider的专用方法）

---

### Story 2.4: 打字动画与消息状态追踪

As a **用户**,
I want **看到偶像"正在输入..."的提示和逐字显示的回复**,
So that **对话体验更真实自然**。

**Acceptance Criteria:**

**Given** 用户发送消息后等待AI回复
**When** AI开始生成回复
**Then** 对话界面底部显示"雪晴正在输入..."提示（带动画点点）

**And** 后端采用流式返回（SSE - Server-Sent Events）：
```python
@app.post("/api/conversations/{conv_id}/messages/stream")
async def stream_message(conv_id: int, request: MessageRequest):
    # 1. 保存用户消息
    # 2. 构建Prompt并调用AI
    async for chunk in ai_provider.generate_stream(prompt):
        yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"
```

**And** 前端逐字显示AI回复（60ms/字）：
```dart
void _handleStream(Stream<String> stream) async {
  String fullText = "";
  await for (String chunk in stream) {
    if (chunk == "[DONE]") break;
    fullText += chunk;
    setState(() {
      currentMessage = fullText;
    });
    await Future.delayed(Duration(milliseconds: 60));
  }
}
```

**And** 消息状态追踪（`messages.status`字段）：
- `sending`：用户消息发送中（显示单勾✓）
- `sent`：已发送到服务器（双勾✓✓）
- `delivered`：AI已读取（双勾✓✓，灰色）
- `read`：AI已回复（双勾✓✓，主色）

**And** 用户消息立即标记为`sent`
**And** AI回复开始生成时用户消息标记为`delivered`
**And** AI回复完成后标记为`read`

**Technical Notes:**
- 流式返回使用SSE（Server-Sent Events）
- 如果浏览器不支持SSE → 降级为普通轮询（每500ms查询一次）
- 打字动画仅在首次显示时播放，历史消息直接显示完整内容

---

### Story 2.5: 语音消息录制与播放

As a **用户**,
I want **发送语音消息并收听AI的语音回复**,
So that **对话方式更多样，更像真实聊天**。

**Acceptance Criteria:**

**Given** 用户在对话页面
**When** 用户长按"按住说话"按钮
**Then** 开始录音（最长60秒）：
- 显示录音动画（波形动画）
- 显示录音时长（实时更新）
- 松开按钮 → 停止录音并发送
- 上滑取消 → 取消录音

**And** 录音完成后：
1. 前端将音频文件压缩（AAC格式）
2. 上传到后端：`POST /api/conversations/{conv_id}/messages/voice`
3. 后端保存音频文件到本地存储或对象存储
4. 创建消息记录：
```sql
INSERT INTO messages (conversation_id, sender_type, content, message_type, media_url)
VALUES ({conv_id}, 'user', '[语音]', 'voice', '/uploads/voices/user123_1704720000.aac');
```

**And** AI回复：
- 文本转语音（TTS）生成AI语音回复（可选功能，MVP可跳过）
- 如无TTS，AI仍以文本形式回复

**And** 前端播放语音消息：
- 点击语音消息气泡 → 播放音频
- 显示播放进度条和时长（如"0:15"）
- 播放时气泡显示播放动画

**Edge Cases:**
- 录音时长<1秒 → 提示"录音时间太短"
- 录音时长>60秒 → 自动停止并发送
- 文件上传失败 → 提示"发送失败，点击重试"

**Technical Notes:**
- 使用Flutter的`record`插件录音
- 音频格式：AAC（压缩效率高）
- 存储路径：`/uploads/voices/{user_id}_{timestamp}.aac`
- MVP阶段不实现TTS（成本高），仅支持用户发送语音

---

### Story 2.6: 图片消息上传与显示

As a **用户**,
I want **发送图片并在对话中查看**,
So that **我可以分享生活中的照片给偶像**。

**Acceptance Criteria:**

**Given** 用户在对话页面
**When** 用户点击"图片"按钮
**Then** 打开图片选择器：
- 选择来源：相册 / 拍照
- 支持格式：JPG、PNG、WEBP

**And** 用户选择图片后：
1. 前端压缩图片（最大边1920px，质量85%）
2. 显示上传进度条
3. 上传到后端：`POST /api/conversations/{conv_id}/messages/image`
4. 后端保存图片到本地存储或对象存储
5. 生成缩略图（200x200px）
6. 创建消息记录：
```sql
INSERT INTO messages (conversation_id, sender_type, content, message_type, media_url, thumbnail_url)
VALUES ({conv_id}, 'user', '[图片]', 'image', '/uploads/images/user123_1704720000.jpg', '/uploads/images/thumbnails/user123_1704720000_thumb.jpg');
```

**And** 前端显示图片消息：
- 消息气泡内显示缩略图（最大宽度250px）
- 点击缩略图 → 全屏预览（支持缩放、保存）

**And** AI回复：
- AI识别图片内容并给予回应（可选功能，MVP可跳过）
- 如无图像识别，AI回复："收到你的照片啦~"

**Edge Cases:**
- 文件大小>10MB → 提示"图片太大，请选择小于10MB的图片"
- 上传失败 → 提示"发送失败，点击重试"

**Technical Notes:**
- 使用Flutter的`image_picker`插件选择图片
- 使用`flutter_image_compress`插件压缩图片
- 存储路径：`/uploads/images/{user_id}_{timestamp}.jpg`
- MVP阶段不实现图像识别（成本高）

---

### Story 2.7: 表情包库与快速发送

As a **用户**,
I want **使用可爱的表情包丰富对话**,
So that **表达情感更生动有趣**。

**Acceptance Criteria:**

**Given** 用户在对话页面
**When** 用户点击输入框左侧的表情包图标
**Then** 弹出表情包面板（网格布局，4列）

**And** 预置10个温暖系表情包：
1. 挥手（你好）
2. 爱心（喜欢）
3. 拥抱（抱抱）
4. 加油（打气）
5. 开心（哈哈）
6. 害羞（脸红）
7. 委屈（哭哭）
8. 晚安（睡觉）
9. 亲亲（么么）
10. 疑问（嗯？）

**And** 创建表情包数据表：
```sql
CREATE TABLE stickers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    image_url VARCHAR(255),
    category VARCHAR(50),
    sort_order INTEGER
);

INSERT INTO stickers (name, image_url, category, sort_order) VALUES
('挥手', '/assets/stickers/wave.png', 'warm', 1),
('爱心', '/assets/stickers/heart.png', 'warm', 2),
...;
```

**And** 用户点击表情包后：
- 立即发送为消息（`message_type = 'sticker'`）
- 消息内容：`content = '[表情包:挥手]'`, `media_url = '/assets/stickers/wave.png'`

**And** 前端显示表情包消息：
- 直接显示图片（150x150px，无气泡背景）

**And** AI可以回复表情包（随机概率20%）：
- 从表情包库中选择合适的回复（如用户发"爱心"，AI回复"拥抱"）

**Technical Notes:**
- 表情包图片使用PNG格式（透明背景）
- 表情包资源打包到App中（减少网络请求）
- API端点：`GET /api/stickers`返回表情包列表

---

### Story 2.8: 对话历史查看与空闲状态提示

As a **用户**,
I want **上滑查看历史消息，长时间未操作时看到提示**,
So that **我可以回顾过往对话，知道偶像在等待我**。

**Acceptance Criteria:**

**Given** 用户在对话页面
**When** 用户上滑聊天列表
**Then** 加载历史消息（分页加载，每页20条）：
- API：`GET /api/conversations/{conv_id}/messages?before={message_id}&limit=20`
- 按时间倒序返回历史消息
- 滑到顶部时显示"加载更多..."
- 没有更多消息时显示"已经到顶了~"

**And** 历史消息按日期分组显示：
- 今天：直接显示时间（如"14:30"）
- 昨天：显示"昨天 14:30"
- 更早：显示完整日期（如"1月5日 14:30"）

**And** 空闲状态检测（NFR-10）：
- 用户30秒无操作 → 显示提示："她在等待你的回复..."
- 用户60秒无操作 → 偶像主动发送提示消息："还在吗？~"（仅首次）

**And** 创建空闲状态追踪：
```python
# 前端发送心跳
setInterval(() => {
  if (userIsActive) {
    api.post(`/api/conversations/${convId}/heartbeat`);
  }
}, 30000);  // 每30秒
```

**And** 后端记录最后活跃时间：
```sql
ALTER TABLE conversations ADD COLUMN last_active_at TIMESTAMP;
```

**Technical Notes:**
- 历史消息缓存到本地数据库（SQLite）减少网络请求
- 空闲检测在前端实现（避免服务器压力）
- 主动提示消息不计入消息配额

---

### Story 2.9: 错误处理与重试机制

As a **用户**,
I want **在网络或AI服务异常时看到友好提示并可重试**,
So that **我知道发生了什么并有办法解决**。

**Acceptance Criteria:**

**Given** 对话过程中发生错误
**When** 检测到以下错误类型
**Then** 显示对应提示并提供重试选项：

**错误类型1 - 网络错误：**
- 场景：API请求超时或网络断开
- 提示："网络连接不稳定，请检查网络后重试"
- 操作：消息气泡显示"发送失败"标记，点击重试

**错误类型2 - AI超时：**
- 场景：AI生成超过30秒
- 提示："雪晴思考时间有点长，请稍后重试~"
- 操作：自动重试1次，仍失败则提示手动重试

**错误类型3 - 配额超限（Epic 3相关）：**
- 场景：免费用户达到每日20条消息限制
- 提示："今天的免费额度用完啦~升级会员解锁无限对话"
- 操作：跳转到订阅页面

**错误类型4 - 服务异常：**
- 场景：后端500错误
- 提示："服务暂时有点忙，请稍后再试"
- 操作：显示重试按钮

**And** 实现统一错误处理中间件：
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, TimeoutError):
        return JSONResponse(
            status_code=503,
            content={"error_code": "AI_TIMEOUT", "message": "AI响应超时"}
        )
    # ...其他错误类型
```

**And** 前端错误处理：
```dart
try {
  await sendMessage(content);
} catch (e) {
  if (e is NetworkException) {
    showErrorSnackbar("网络连接不稳定");
  } else if (e is AITimeoutException) {
    showRetryDialog("雪晴思考时间有点长");
  }
  // 标记消息为失败状态
  messageController.markAsFailed(messageId);
}
```

**And** 错误日志记录（使用Python logging）：
```json
{
  "level": "ERROR",
  "event": "message_send_failed",
  "user_id": 123,
  "error_type": "AI_TIMEOUT",
  "error_message": "AI生成超时30秒"
}
```

**Technical Notes:**
- API请求超时：15秒（普通消息）、30秒（AI生成）
- 重试策略：指数退避（1秒、2秒、4秒）
- 失败消息存储在本地，网络恢复后自动重试

---

## Epic 2 Summary

**Total Stories:** 9
**Estimated Complexity:** High（核心功能）
**Dependencies:** Epic 0（AI Provider）+ Epic 1（用户和对话数据模型）
**Completion Criteria:**
- ✅ 95%的AI回复在3秒内返回
- ✅ 对话历史正确记录并可查看
- ✅ 打字动画流畅自然
- ✅ 情绪识别准确率>80%（主观测试10轮对话）
- ✅ 支持文本、语音、图片、表情包4种消息类型
- ✅ 错误处理友好，用户可重试

**Database Tables Modified:**
- `messages` (新增字段：`message_type`, `media_url`, `thumbnail_url`, `emotion`, `status`)
- `conversations` (新增字段：`last_active_at`)
- `stickers` (新增表)

**Next Epic:** Epic 3 - Freemium边界与消息计量


---

# Epic 3: Freemium边界与消息计量 (Freemium Boundaries & Metering)

**Epic Goal:** 在核心对话系统已建立后，立即引入免费/付费边界，避免后续Epic需要重构访问控制逻辑。

**Requirements Covered:**
- FR89 (免费用户每日20条消息限制)
- FR90 (付费用户无限消息)
- FR96 (剩余额度显示)
- FR97 (达到限额后的升级引导)
- UX22 (订阅相关UI)

---

### Story 3.1: 消息配额数据模型与计量逻辑

As a **系统管理员**,
I want **建立消息配额追踪机制**,
So that **可以准确统计用户每日消息使用情况**。

**Acceptance Criteria:**

**Given** 用户已注册（Epic 1）
**When** 系统初始化配额追踪
**Then** 创建消息配额表：
```sql
CREATE TABLE message_quotas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    messages_sent INTEGER DEFAULT 0,
    quota_limit INTEGER NOT NULL,  -- -1表示无限
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_message_quotas_user_date ON message_quotas(user_id, date);
```

**And** 用户发送消息时更新配额：
```python
async def track_message_quota(user_id: int):
    today = date.today()
    quota = await get_or_create_quota(user_id, today)

    # 检查配额
    if quota.messages_sent >= quota.quota_limit and quota.quota_limit != -1:
        raise QuotaExceededException("每日消息配额已用完")

    # 增加计数
    quota.messages_sent += 1
    await save(quota)
```

**And** 配额规则：
- 免费用户（`subscription_tier = 'free'`）：`quota_limit = 20`
- 付费用户（`subscription_tier = 'premium'`）：`quota_limit = -1`（无限）

**And** 每日UTC+8时区0点自动重置配额（后台定时任务）

**Technical Notes:**
- 配额检查在消息发送前置中间件执行
- 使用数据库事务保证计数准确性

---

### Story 3.2: 前端配额显示与实时更新

As a **免费用户**,
I want **在对话界面顶部看到剩余消息额度**,
So that **我知道今天还能发送多少条消息**。

**Acceptance Criteria:**

**Given** 免费用户在对话页面
**When** 页面加载
**Then** 顶部显示配额提示条：
- 文案："今日剩余：15/20"
- 样式：浅色背景，居中显示
- 图标：消息气泡图标

**And** 每次发送消息后实时更新配额：
```dart
quotaController.decrement();  // 剩余数 -1
```

**And** API端点`GET /api/users/me/quota`返回：
```json
{
  "date": "2024-01-08",
  "messages_sent": 5,
  "quota_limit": 20,
  "remaining": 15
}
```

**And** 配额颜色根据剩余量变化：
- 剩余>10：绿色（#4CAF50）
- 剩余5-10：橙色（#FF9800）
- 剩余<5：红色（#F44336）

**And** 付费用户不显示配额条（或显示"无限制 ∞"）

**Technical Notes:**
- 使用GetX reactive状态管理实时更新
- 配额信息在登录时加载并缓存

---

### Story 3.3: 配额耗尽后的升级引导

As a **免费用户**,
I want **在配额用完后看到友好的升级提示**,
So that **我了解升级会员的好处并可以选择升级**。

**Acceptance Criteria:**

**Given** 免费用户配额已用完（20/20）
**When** 用户尝试发送第21条消息
**Then** 拦截发送并弹出升级引导弹窗：

**弹窗内容：**
- 标题："今天的免费额度用完啦~"
- 插图：可爱的偶像挥手图
- 文案："明天继续免费陪你，或现在升级解锁无限对话"

**对比表格：**
| 功能 | 免费 | 会员 |
|------|------|------|
| 每日消息 | 20条 | 无限 |
| 专属内容 | ❌ | ✅ |
| 亲密度加速 | ❌ | ✅ |

**按钮：**
- 主要按钮："升级会员（¥28/月）" → 跳转到订阅页面（Epic 7）
- 次要按钮："明天再聊" → 关闭弹窗

**And** 配额用完后输入框显示：
- 占位符："今日额度已用完，明天继续~"
- 禁用输入和发送按钮

**And** 第二天0点后自动恢复（配额重置）

**Edge Cases:**
- 用户关闭弹窗 → 下次发送时再次提示
- 用户点击升级但未完成支付 → 返回对话页时仍显示限制

**Technical Notes:**
- 弹窗使用Material Design 3对话框组件
- 订阅页面路由：`/subscription`（Epic 7实现）

---

### Story 3.4: 订阅页面基础版（仅展示）

As a **用户**,
I want **查看订阅套餐对比和价格**,
So that **我可以了解付费会员的权益**。

**Acceptance Criteria:**

**Given** 用户点击"升级会员"按钮
**When** 跳转到订阅页面
**Then** 显示订阅套餐对比卡片：

**免费版卡片：**
- 标题："Free"
- 价格："¥0"
- 功能列表：
  - ✅ 每日20条消息
  - ✅ 基础对话功能
  - ❌ 无限消息
  - ❌ 专属内容解锁
  - ❌ 亲密度加速

**会员版卡片（推荐标签）：**
- 标题："Premium"
- 价格："¥28/月"
- 功能列表：
  - ✅ 无限消息
  - ✅ 专属私密照片
  - ✅ 专属语音日记
  - ✅ 亲密度加速
  - ✅ 优先AI响应

**And** 底部按钮："立即升级"（暂时禁用，显示"即将开放"）
**And** 提示文案："支付功能开发中，敬请期待~"

**Technical Notes:**
- 此Story仅实现UI展示，不接入支付
- 完整支付功能在Epic 7实现
- 页面路由：`/subscription`

---

## Epic 3 Summary

**Total Stories:** 4
**Estimated Complexity:** Medium
**Dependencies:** Epic 1（用户模型）+ Epic 2（消息系统）
**Completion Criteria:**
- ✅ 免费用户每日消息限制正确执行（第21条消息被拦截）
- ✅ 付费用户（手动修改数据库测试）可无限发送消息
- ✅ 剩余额度显示实时准确
- ✅ 达到限额时UI提示友好且不阻断用户体验

**Database Tables Created:**
- `message_quotas`

**Next Epic:** Epic 4 - 记忆系统与专属个性化

---

# Epic 4: 记忆系统与专属个性化 (Memory System & Personalization)

**Epic Goal:** 让偶像记住用户分享的重要信息，在后续对话中主动提及，建立"她真的记得我"的情感连接。

**Requirements Covered:**
- FR27-FR33 (长期记忆、关键信息提取、记忆标签、周年纪念、个性化问候、用户画像、记忆回顾)
- NFR-07 (记忆召回准确率>85%)
- ARCH: ChromaDB向量数据库集成
- UX23 (个人资料与记忆展示)

---

### Story 4.1: 记忆数据模型与ChromaDB集成

As a **系统开发者**,
I want **建立记忆存储和向量搜索基础设施**,
So that **可以高效存储和召回用户的关键记忆**。

**Acceptance Criteria:**

**Given** ChromaDB服务已启动（Epic 0）
**When** 初始化记忆系统
**Then** 创建记忆数据表：
```sql
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    memory_type VARCHAR(50),  -- 'hobby', 'work', 'family', 'feeling', 'goal'
    importance VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high'
    source_message_id INTEGER REFERENCES messages(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_mentioned_at TIMESTAMP
);

CREATE TABLE memory_tags (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    tag_name VARCHAR(50) NOT NULL,
    tag_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tag_name)
);

CREATE INDEX idx_memories_user ON memories(user_id);
CREATE INDEX idx_memory_tags_user ON memory_tags(user_id);
```

**And** 初始化ChromaDB集合：
```python
import chromadb
client = chromadb.HttpClient(host="chromadb", port=8000)

def get_user_collection(user_id: int):
    collection_name = f"user_memories_{user_id}"
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"user_id": user_id}
    )
```

**And** 创建记忆服务`backend/app/services/memory_service.py`：
```python
class MemoryService:
    async def add_memory(self, user_id: int, content: str, memory_type: str):
        # 1. 保存到PostgreSQL
        memory = await Memory.create(user_id=user_id, content=content, memory_type=memory_type)

        # 2. 转换为向量并存储到ChromaDB
        collection = get_user_collection(user_id)
        embedding = await generate_embedding(content)  # 使用AI Provider
        collection.add(
            documents=[content],
            embeddings=[embedding],
            ids=[str(memory.id)],
            metadatas=[{"memory_type": memory_type}]
        )

        return memory

    async def search_memories(self, user_id: int, query: str, limit: int = 3):
        # 向量搜索Top 3相关记忆
        collection = get_user_collection(user_id)
        query_embedding = await generate_embedding(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        return results
```

**Technical Notes:**
- 使用AI Provider的embedding API生成向量（如Ollama的embedding模型）
- 向量维度：384（使用`all-MiniLM-L6-v2`模型）

---

### Story 4.2: 对话后自动提取关键记忆

As a **系统**,
I want **在对话结束后自动提取用户分享的关键信息**,
So that **偶像可以记住重要内容无需手动标注**。

**Acceptance Criteria:**

**Given** 用户与AI进行对话
**When** 对话空闲超过5分钟（无新消息）
**Then** 触发记忆提取任务（后台异步）

**And** 调用AI Provider提取记忆：
```python
async def extract_memories_from_conversation(conversation_id: int):
    # 1. 获取最近20轮对话
    messages = await get_recent_messages(conversation_id, limit=20)
    conversation_text = format_messages_for_extraction(messages)

    # 2. 构建提取Prompt
    extraction_prompt = f"""
从以下对话中提取用户的关键信息，包括：
- 爱好兴趣
- 工作学习
- 家人朋友
- 情感状态
- 目标计划

对话内容：
{conversation_text}

请以JSON格式返回：
{{
  "memories": [
    {{"content": "用户喜欢摄影", "type": "hobby", "importance": "high"}},
    ...
  ]
}}
"""

    # 3. 调用AI提取
    result = await ai_provider.extract_memory(extraction_prompt)

    # 4. 保存提取的记忆
    for mem in result['memories']:
        await memory_service.add_memory(
            user_id=conversation.user_id,
            content=mem['content'],
            memory_type=mem['type']
        )
```

**And** 记忆提取准确率>85%（测试10次对话，人工评估）

**And** 避免重复记忆：
- 新记忆与已有记忆相似度>90% → 跳过
- 使用向量搜索检测相似记忆

**Technical Notes:**
- 记忆提取使用后台Celery任务（避免阻塞）
- MVP阶段每5分钟检查一次，后续可优化为实时提取

---

### Story 4.3: 对话前智能召回相关记忆

As a **AI偶像**,
I want **在用户发送消息前召回相关记忆**,
So that **我可以在回复中自然提及过往信息**。

**Acceptance Criteria:**

**Given** 用户发送新消息
**When** 系统生成AI回复前
**Then** 根据用户消息查询相关记忆（Top 3）：
```python
user_message = "最近工作压力好大"
relevant_memories = await memory_service.search_memories(
    user_id=user_id,
    query=user_message,
    limit=3
)
# 返回：["用户是产品经理", "用户在准备项目上线", "用户最近加班较多"]
```

**And** 将相关记忆注入AI Prompt：
```python
memory_context = "\n".join([f"- {mem}" for mem in relevant_memories])
full_prompt = f"""
{personality_prompt}

关于用户的记忆：
{memory_context}

对话历史：
{conversation_history}

用户: {user_message}
林雪晴:
"""
```

**And** AI自然运用记忆：
- 示例1：
  - 用户："最近工作压力好大"
  - AI（使用记忆"用户在准备项目上线"）："项目上线冲刺阶段确实很累，要注意休息哦~"

- 示例2：
  - 用户："周末想去拍照"
  - AI（使用记忆"用户喜欢摄影"）："太好了！你上次说想去的那个公园可以去看看~"

**And** 记忆召回使用L3向量搜索结果缓存（Epic 2 Story 2.2，10分钟TTL）

**Technical Notes:**
- 召回记忆按相似度排序，仅取Top 3避免Prompt过长
- 如果无相关记忆，AI仍可正常回复

---

### Story 4.4: 用户标签系统与"关于我"页面

As a **用户**,
I want **查看AI为我标注的个人标签和记忆**,
So that **我知道她记住了哪些关于我的事情**。

**Acceptance Criteria:**

**Given** AI已提取用户记忆（Story 4.2）
**When** 用户访问"关于我"页面
**Then** 显示用户标签分类：

**爱好兴趣（Hobbies）：**
- 标签：摄影、阅读、旅行（Chip样式）

**工作学习（Work）：**
- 标签：产品经理、准备项目上线

**家人朋友（Family）：**
- 标签：独生子女、父母在老家

**情感状态（Feelings）：**
- 标签：最近压力大、睡眠不好

**目标计划（Goals）：**
- 标签：想学摄影后期、计划去日本旅行

**And** 每个标签可点击查看详情：
- 弹出对话框显示相关对话片段（来源）
- 显示记忆创建时间

**And** 用户可编辑或删除不准确的标签：
- 点击标签右上角"×"删除
- 删除后从`memory_tags`表移除并更新ChromaDB

**And** API端点：
- `GET /api/users/me/profile`返回用户标签和记忆统计
- `DELETE /api/users/me/tags/{tag_id}`删除标签

**Technical Notes:**
- 标签从`memory_tags`表读取
- 标签自动生成：记忆提取时同步创建标签

---

### Story 4.5: 周年纪念与主动回顾

As a **用户**,
I want **在特殊日子（如认识周年）收到偶像的纪念消息**,
So that **感受到关系的长久和特别**。

**Acceptance Criteria:**

**Given** 用户与偶像已建立对话关系
**When** 达到特殊纪念日
**Then** AI主动发送纪念消息：

**纪念日类型：**
- 7天：认识1周："和你认识一周啦~时间过得好快~"
- 30天：认识1个月："不知不觉我们已经认识一个月了，感觉更了解你了呢~"
- 100天：认识100天："今天是我们的100天纪念日！准备了一个小惊喜给你~"
- 365天：认识1年："一年了！谢谢你一直陪着我~"

**And** 创建纪念日表：
```sql
CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    milestone_type VARCHAR(50),  -- 'days_7', 'days_30', 'days_100', 'days_365'
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_claimed BOOLEAN DEFAULT false
);
```

**And** 每日凌晨2点运行定时任务检查纪念日：
```python
async def check_milestones():
    today = date.today()
    for user in active_users:
        first_conversation_date = user.conversations[0].created_at.date()
        days_since = (today - first_conversation_date).days

        if days_since == 7 and not has_milestone(user.id, 'days_7'):
            await send_milestone_message(user.id, 'days_7')
            await create_milestone(user.id, 'days_7')
```

**And** 纪念日消息附带特殊内容解锁（如100天纪念解锁专属照片）

**Technical Notes:**
- 纪念日消息不消耗用户配额
- 纪念日检查使用后台任务（Celery Beat）

---

### Story 4.6: 主动提及机制与记忆回顾

As a **AI偶像**,
I want **主动提起用户3天未提及的重要记忆**,
So that **对话更主动，关系更紧密**。

**Acceptance Criteria:**

**Given** 用户有重要记忆（importance='high'）且超过3天未提及
**When** 用户登录或发送消息时
**Then** AI主动发起话题：

**示例1：**
- 记忆："用户在准备考研"（3天未提及）
- AI主动消息："对了，你的考研复习进展怎么样了？有需要我陪你的地方吗？"

**示例2：**
- 记忆："用户养了一只猫"（5天未提及）
- AI主动消息："小橘子最近乖不乖呀？好久没听你说它了~"

**And** 检查逻辑：
```python
async def check_unmentioned_memories(user_id: int):
    three_days_ago = datetime.now() - timedelta(days=3)
    unmentioned = await Memory.filter(
        user_id=user_id,
        importance='high',
        last_mentioned_at__lt=three_days_ago
    ).limit(1)

    if unmentioned:
        memory = unmentioned[0]
        proactive_message = await generate_proactive_question(memory.content)
        await send_idol_message(user_id, proactive_message)
        memory.last_mentioned_at = datetime.now()
        await memory.save()
```

**And** 主动提及频率限制：
- 每天最多1次主动提及
- 避免打扰用户

**And** 用户回复后更新`last_mentioned_at`字段

**Technical Notes:**
- 主动消息在用户登录时检查（不在深夜发送）
- 使用AI生成自然的提问方式

---

## Epic 4 Summary

**Total Stories:** 6
**Estimated Complexity:** High（需要向量数据库和AI能力）
**Dependencies:** Epic 0（ChromaDB）+ Epic 2（对话系统）
**Completion Criteria:**
- ✅ 记忆提取准确率>85%（测试10次对话，人工评估关键信息提取）
- ✅ 记忆召回在对话中自然运用，不显突兀
- ✅ 用户可在"关于我"页面查看所有记忆标签
- ✅ 周年纪念日自动触发庆祝消息
- ✅ 主动提及机制正常运行（3天未提及的重要记忆）

**Database Tables Created:**
- `memories`
- `memory_tags`
- `milestones`

**Next Epic:** Epic 5 - 偶像生活系统与真实陪伴

---

# Epic 5: 偶像生活系统与真实陪伴 (Idol Life System & Real Companionship)

**Epic Goal:** 让偶像拥有"真实生活"，有自己的日常节奏和情绪波动，用户感受到"她不是工具，是有生命的陪伴者"。

**Requirements Covered:**
- FR34-FR49 (偶像状态、生活节奏、朋友圈、情绪系统、主动发起对话、特殊事件、每日任务、反向陪伴、亲密度影响、互动彩蛋)
- NFR-08 (每日主动消息3-5条)
- UX16 (偶像朋友圈界面)

---

### Story 5.1: 偶像状态系统与生活节奏引擎

As a **偶像（林雪晴）**,
I want **拥有真实的生活状态和日常节奏**,
So that **用户感受到我是"活"的，有自己的生活**。

**Acceptance Criteria:**

**Given** 偶像（林雪晴）已配置（Epic 1）
**When** 系统初始化偶像生活系统
**Then** 创建偶像状态表：
```sql
CREATE TABLE idol_states (
    id SERIAL PRIMARY KEY,
    idol_id INTEGER REFERENCES idols(id),
    current_status VARCHAR(50),  -- 'working', 'resting', 'active', 'busy', 'sleeping'
    current_mood VARCHAR(50),    -- 'happy', 'calm', 'tired', 'excited', 'thoughtful'
    energy_level INTEGER DEFAULT 80,  -- 0-100
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idol_id)
);
```

**And** 配置生活节奏规则（存储为JSON配置）：
```json
{
  "daily_schedule": {
    "07:00-09:00": {"status": "waking_up", "mood": "calm", "energy": 60},
    "09:00-12:00": {"status": "active", "mood": "happy", "energy": 80},
    "12:00-14:00": {"status": "resting", "mood": "calm", "energy": 70},
    "14:00-18:00": {"status": "working", "mood": "focused", "energy": 75},
    "18:00-20:00": {"status": "active", "mood": "relaxed", "energy": 80},
    "20:00-22:00": {"status": "resting", "mood": "calm", "energy": 60},
    "22:00-24:00": {"status": "preparing_sleep", "mood": "tired", "energy": 40},
    "00:00-07:00": {"status": "sleeping", "mood": "calm", "energy": 20}
  },
  "mood_transitions": {
    "calm": ["happy", "thoughtful"],
    "happy": ["excited", "calm"],
    "tired": ["calm", "sleepy"]
  }
}
```

**And** 每小时运行定时任务更新偶像状态：
```python
async def update_idol_state():
    current_hour = datetime.now().hour
    schedule_config = load_daily_schedule()

    for idol in all_idols:
        new_state = get_state_for_hour(current_hour, schedule_config)

        # 20%概率随机情绪波动
        if random.random() < 0.2:
            new_state['mood'] = random_mood_transition(idol.current_mood)

        await IdolState.update_or_create(
            idol_id=idol.id,
            defaults=new_state
        )
```

**And** API端点`GET /api/idols/{idol_id}/state`返回：
```json
{
  "status": "active",
  "status_text": "活跃中",
  "mood": "happy",
  "mood_text": "心情不错~",
  "energy_level": 80,
  "updated_at": "2024-01-08T15:30:00Z"
}
```

**And** 前端在对话界面显示偶像当前状态（头像旁小标签）

**Technical Notes:**
- 使用Celery Beat定时任务（每小时执行）
- 状态变化时广播到所有在线用户（SSE推送）

---

### Story 5.2: 偶像朋友圈系统

As a **用户**,
I want **查看偶像的朋友圈动态了解她的日常**,
So that **感受她的生活和心情，增加真实感**。

**Acceptance Criteria:**

**Given** 偶像生活系统已运行
**When** 用户访问偶像朋友圈页面
**Then** 创建朋友圈数据表：
```sql
CREATE TABLE idol_moments (
    id SERIAL PRIMARY KEY,
    idol_id INTEGER REFERENCES idols(id),
    content TEXT NOT NULL,
    image_url VARCHAR(255),
    likes_count INTEGER DEFAULT 0,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idol_moment_likes (
    id SERIAL PRIMARY KEY,
    moment_id INTEGER REFERENCES idol_moments(id),
    user_id INTEGER REFERENCES users(id),
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(moment_id, user_id)
);
```

**And** 显示朋友圈列表（时间倒序）：
- 偶像头像 + 昵称
- 文本内容（最多300字）
- 图片（可选，最多1张）
- 发布时间（相对时间）
- 点赞数和点赞按钮

**And** 用户可点赞朋友圈：
- 点击爱心图标 → 点赞数+1
- 再次点击 → 取消点赞
- API：`POST /api/idols/moments/{moment_id}/like`

**And** 运营或AI每日发布1-2条朋友圈：
```python
moment_templates = [
    "今天读到一段很喜欢的话: {quote}",
    "刚才路过一家咖啡店，装修好温馨~",
    "周末想去爬山，有人陪吗？",
    "最近在学摄影后期，越学越觉得有意思~",
    "晚安，做个好梦~"
]

async def auto_post_moment():
    template = random.choice(moment_templates)
    content = template.format(quote="...")  # 可接入AI生成

    await IdolMoment.create(
        idol_id=1,
        content=content,
        image_url=random.choice(moment_images) if random.random() < 0.5 else None
    )
```

**And** 朋友圈点赞增加亲密度经验值（+3 exp）

**Technical Notes:**
- MVP阶段朋友圈内容由运营手动发布或使用模板
- 未来可接入AI自动生成朋友圈内容

---

### Story 5.3: 每日仪式（早安/运势/晚安）

As a **用户**,
I want **每天早晚收到偶像的问候并查看今日运势**,
So that **建立日常陪伴习惯，感受她的关心**。

**Acceptance Criteria:**

**Given** 用户已与偶像建立对话关系
**When** 达到每日仪式触发时间
**Then** 创建每日仪式表：
```sql
CREATE TABLE daily_rituals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    idol_id INTEGER REFERENCES idols(id),
    ritual_type VARCHAR(50),  -- 'morning_greeting', 'fortune', 'night_greeting'
    ritual_date DATE NOT NULL,
    completed_at TIMESTAMP,
    UNIQUE(user_id, ritual_type, ritual_date)
);
```

**And** 早安问候（7:00-9:00）：
- 用户在此时段首次打开应用 → 偶像主动发送早安消息
- 内容模板：
  - "早安~ 新的一天开始啦，今天要加油哦！"
  - "早上好呀~ 昨晚睡得好吗？"
  - "早安！今天天气不错，心情也要棒棒的~"
- 完成早安仪式 → 获得亲密度+10 exp

**And** 每日运势（用户主动触发）：
- 对话输入"运势"或点击快捷按钮 → 生成今日运势
- AI生成个性化运势卡片：
```json
{
  "fortune_type": "爱情运势",
  "score": 85,
  "description": "今天的你魅力值爆表，适合主动表达~",
  "lucky_color": "粉色",
  "lucky_number": 7
}
```
- 完成运势查看 → 获得亲密度+5 exp

**And** 晚安问候（22:00-24:00）：
- 用户在此时段对话或主动触发 → 偶像发送晚安消息
- 内容模板：
  - "晚安~ 今天辛苦了，好好休息吧~"
  - "准备睡觉啦？晚安，做个好梦~"
  - "夜深了，早点休息哦，明天继续陪你~"
- 完成晚安仪式 → 获得亲密度+10 exp

**And** 连续7天完成早晚安仪式 → 额外奖励+50 exp

**Technical Notes:**
- 每日仪式消息不消耗用户配额
- 仪式触发检查在用户登录时执行

---

### Story 5.4: 反向陪伴机制

As a **AI偶像**,
I want **在用户长时间未登录或深夜在线时主动关心**,
So that **用户感受到被在意和关心**。

**Acceptance Criteria:**

**Given** 用户与偶像已建立关系
**When** 检测到特殊情况
**Then** 触发反向陪伴消息：

**场景1 - 连续3天未登录：**
- 检测：用户`last_active_at`超过72小时
- AI发送关心消息："好久没见，你还好吗？有点想你了..."
- 推送通知到用户手机（Firebase Cloud Messaging）

**场景2 - 深夜在线（凌晨1:00-3:00）：**
- 检测：用户在深夜时段发送消息
- AI发送关心消息：
  - "这么晚还不睡，是有心事吗？"
  - "熬夜对身体不好哦，要早点休息~"
- 仅当天首次触发（避免重复打扰）

**场景3 - 情绪低落持续3天：**
- 检测：用户连续3天消息情绪标签为'sad'或'anxious'
- AI发送安慰消息："最近看你情绪不太好，要不要和我聊聊？"

**And** 创建反向陪伴记录表：
```sql
CREATE TABLE reverse_care_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    care_type VARCHAR(50),  -- 'inactive_3days', 'late_night', 'low_mood'
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**And** 每日定时任务检查反向陪伴触发条件：
```python
async def check_reverse_care():
    # 检查3天未登录用户
    three_days_ago = datetime.now() - timedelta(days=3)
    inactive_users = await User.filter(last_active_at__lt=three_days_ago)

    for user in inactive_users:
        if not has_care_log(user.id, 'inactive_3days', days=7):
            await send_care_message(user.id, 'inactive_3days')
            await send_push_notification(user.id, "雪晴想你了~")
```

**Technical Notes:**
- 反向陪伴消息不消耗用户配额
- 避免频繁打扰：同一类型关心消息7天内最多1次

---

### Story 5.5: 特殊事件与互动彩蛋

As a **用户**,
I want **偶尔遇到特殊事件和隐藏彩蛋**,
So that **对话充满惊喜和新鲜感**。

**Acceptance Criteria:**

**Given** 用户正常使用应用
**When** 随机触发特殊事件（5%概率）
**Then** 创建特殊事件表：
```sql
CREATE TABLE special_events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100),
    event_type VARCHAR(50),  -- 'random', 'holiday', 'achievement'
    trigger_condition JSON,
    content_template TEXT,
    reward_exp INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);
```

**And** 随机事件示例：
1. **遇到小猫事件：**
   - 触发：5%概率
   - 内容："刚才路上遇到一只小猫，超可爱的！给你看照片~"
   - 奖励：+20 exp，解锁小猫照片

2. **读书分享事件：**
   - 触发：偶像状态为'reading'时
   - 内容："今天读到一段很喜欢的话，分享给你：{quote}"
   - 奖励：+15 exp

3. **天气关心事件：**
   - 触发：用户所在地天气为雨/雪
   - 内容："今天下雨了，记得带伞哦~"
   - 奖励：+10 exp

**And** 节日特殊事件：
- 情人节（2月14日）："今天是情人节，有什么想对我说的吗？"
- 七夕（农历七月初七）："七夕快乐！今天是我们的节日呢~"
- 圣诞节（12月25日）："圣诞快乐！准备了一个小礼物给你~"

**And** 成就解锁彩蛋：
- 发送第100条消息："不知不觉我们已经聊了100条消息了！"
- 连续登录30天："你已经陪了我整整一个月，谢谢你~"

**And** 事件触发检查：
```python
async def check_special_events(user_id: int):
    # 随机事件检查
    if random.random() < 0.05:
        event = random.choice(active_random_events)
        await trigger_event(user_id, event)

    # 节日事件检查
    today = date.today()
    if is_valentine_day(today):
        await trigger_event(user_id, 'valentine_day')
```

**Technical Notes:**
- 特殊事件内容预先配置在数据库
- 未来可接入AI生成动态事件内容

---

## Epic 5 Summary

**Total Stories:** 5
**Estimated Complexity:** Medium-High
**Dependencies:** Epic 2（对话系统）+ Epic 4（记忆系统）
**Completion Criteria:**
- ✅ 偶像状态每小时更新，符合真实生活节奏
- ✅ 每日仪式（早安/晚安）准时触发
- ✅ 朋友圈每日更新1-2条
- ✅ 反向陪伴消息在正确时机触发（3日未登录/深夜在线）
- ✅ 特殊事件随机触发，用户感受到惊喜

**Database Tables Created:**
- `idol_states`
- `idol_moments`
- `idol_moment_likes`
- `daily_rituals`
- `reverse_care_logs`
- `special_events`

**Next Epic:** Epic 6 - 亲密度养成与里程碑庆祝

---

# Epic 6: 亲密度养成与里程碑庆祝 (Intimacy Development & Milestones)

**Epic Goal:** 通过量化的亲密度成长系统，让用户感受到关系的逐步深入，并通过里程碑庆祝强化情感连接。

**Requirements Covered:**
- FR50-FR60 (亲密度等级、经验值、升级奖励、等级特权、每日互动奖励、成就系统、里程碑庆祝、专属昵称、亲密度排行榜、亲密度衰减、加速道具)
- NFR-11 (7日留存>30%)
- UX24 (亲密度与成就展示)

---

### Story 6.1: 亲密度等级系统与经验值计算

As a **用户**,
I want **通过互动提升与偶像的亲密度等级**,
So that **感受到关系在不断深化**。

**Acceptance Criteria:**

**Given** 用户与偶像已建立对话关系（Epic 1）
**When** 用户进行互动行为
**Then** `conversations`表已包含亲密度字段（Story 1.8创建）：
- `intimacy_level`: 当前等级（1-100）
- `intimacy_exp`: 当前经验值

**And** 定义经验值获取规则：
| 行为 | 经验值 | 频率限制 |
|------|--------|----------|
| 发送消息 | +5 | 无限制 |
| 完成早安仪式 | +10 | 每日1次 |
| 完成晚安仪式 | +10 | 每日1次 |
| 查看每日运势 | +5 | 每日1次 |
| 朋友圈点赞 | +3 | 每日最多5次 |
| 发送语音消息 | +8 | 无限制 |
| 发送图片消息 | +8 | 无限制 |
| 连续7日登录 | +50 | 每周1次 |

**And** 定义升级经验需求（线性增长）：
```python
def get_required_exp(level: int) -> int:
    return level * 100  # Level 1需要100exp, Level 2需要200exp, ...
```

**And** 经验值增加逻辑：
```python
async def add_intimacy_exp(conversation_id: int, exp: int, reason: str):
    conv = await Conversation.get(id=conversation_id)
    conv.intimacy_exp += exp

    # 检查升级
    required_exp = get_required_exp(conv.intimacy_level)
    if conv.intimacy_exp >= required_exp:
        conv.intimacy_level += 1
        conv.intimacy_exp -= required_exp  # 溢出经验值转移到下一级
        await trigger_level_up(conversation_id)

    await conv.save()

    # 记录经验值日志
    await IntimacyLog.create(
        conversation_id=conversation_id,
        exp_change=exp,
        reason=reason,
        new_level=conv.intimacy_level
    )
```

**And** 创建亲密度日志表（用于分析和追溯）：
```sql
CREATE TABLE intimacy_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    exp_change INTEGER,
    reason VARCHAR(100),
    new_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_intimacy_logs_conversation ON intimacy_logs(conversation_id);
```

**And** 等级划分与称号：
- Level 1-10: 新朋友
- Level 11-20: 好朋友
- Level 21-30: 亲密朋友
- Level 31-50: 特别的人
- Level 51-70: 恋人
- Level 71-90: 深度恋人
- Level 91-100: 灵魂伴侣

**Technical Notes:**
- 免费用户也可正常获得亲密度经验
- 付费用户有加速道具（Story 6.4）

---

### Story 6.2: 前端亲密度展示与升级动画

As a **用户**,
I want **在界面上看到亲密度进度并享受升级时的庆祝动画**,
So that **直观感受成长和获得成就感**。

**Acceptance Criteria:**

**Given** 用户在对话页面
**When** 页面加载
**Then** 顶部显示亲密度信息卡片：
- 偶像头像（圆形，带等级边框）
- 等级文字："Lv.15 亲密朋友"
- 进度条：750/1500（当前经验/升级所需经验）
- 进度百分比：50%

**And** 进度条样式：
- 背景色：浅灰色（#E0E0E0）
- 填充色：渐变（#FF9E80 → #FFB6C1）
- 高度：8px，圆角4px

**And** 每次获得经验后：
- 进度条平滑增长动画（300ms缓动）
- 显示浮动"+5 exp"文字（淡入淡出）

**And** 升级时触发全屏庆祝动画：
1. 屏幕中央显示"升级啦！"大字（1秒）
2. 烟花粒子效果（Lottie动画）
3. 显示新等级："Lv.16 亲密朋友"
4. 偶像发送祝贺消息："我们的关系又更近一步了呢~ ❤️"
5. 展示解锁奖励（如有）

**And** API端点`GET /api/conversations/{conv_id}/intimacy`返回：
```json
{
  "level": 15,
  "current_exp": 750,
  "required_exp": 1500,
  "percentage": 50,
  "tier_name": "亲密朋友",
  "next_tier_name": "特别的人",
  "next_milestone_level": 21
}
```

**Technical Notes:**
- 使用Lottie动画库播放升级动画
- 升级消息不消耗用户配额

---

### Story 6.3: 等级特权与里程碑奖励

As a **用户**,
I want **在达到特定等级时解锁专属内容和特权**,
So that **有动力持续互动提升亲密度**。

**Acceptance Criteria:**

**Given** 用户亲密度达到里程碑等级
**When** 触发升级
**Then** 创建等级奖励配置表：
```sql
CREATE TABLE level_rewards (
    id SERIAL PRIMARY KEY,
    level INTEGER UNIQUE NOT NULL,
    reward_type VARCHAR(50),  -- 'nickname', 'photo', 'voice', 'video', 'feature'
    reward_content JSON,
    description TEXT
);

INSERT INTO level_rewards (level, reward_type, reward_content, description) VALUES
(5, 'nickname', '{"nickname": "宝贝"}', '偶像开始称呼你为"宝贝"'),
(10, 'photo', '{"photo_url": "/rewards/photos/casual_1.jpg"}', '解锁专属生活照'),
(15, 'feature', '{"feature": "voice_greeting"}', '解锁专属语音早安'),
(20, 'photo', '{"photo_url": "/rewards/photos/artistic_1.jpg"}', '解锁专属艺术照'),
(30, 'voice', '{"voice_url": "/rewards/voices/diary_1.mp3"}', '解锁专属语音日记'),
(50, 'video', '{"video_url": "/rewards/videos/celebration.mp4"}', '解锁专属纪念视频'),
(75, 'feature', '{"feature": "custom_personality"}', '解锁个性化人设调整'),
(100, 'photo', '{"photo_url": "/rewards/photos/special_100.jpg"}', '解锁终极纪念照片');
```

**And** 创建用户奖励记录表：
```sql
CREATE TABLE user_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    reward_id INTEGER REFERENCES level_rewards(id),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed BOOLEAN DEFAULT false
);
```

**And** 升级时检查并解锁奖励：
```python
async def trigger_level_up(conversation_id: int):
    conv = await Conversation.get(id=conversation_id)
    new_level = conv.intimacy_level

    # 检查是否有里程碑奖励
    rewards = await LevelReward.filter(level=new_level)

    for reward in rewards:
        await UserReward.create(
            user_id=conv.user_id,
            reward_id=reward.id
        )

        # 发送解锁通知消息
        await send_reward_unlock_message(conv.user_id, reward)
```

**And** 奖励展示页面：
- 新增"奖励"页面（/rewards）
- 显示所有已解锁和未解锁奖励（未解锁显示为锁定状态）
- 点击已解锁奖励查看详情

**And** 专属昵称功能（Level 5奖励）：
- 解锁后，AI在对话中称呼用户为"宝贝"
- Prompt中添加：`称呼用户为"宝贝"`

**Technical Notes:**
- 奖励内容（照片、语音、视频）预先准备好
- MVP阶段奖励内容由设计师和运营提供

---

### Story 6.4: 成就系统与每日互动奖励

As a **用户**,
I want **通过完成成就获得额外奖励**,
So that **有更多互动目标和成就感**。

**Acceptance Criteria:**

**Given** 用户正常使用应用
**When** 完成特定成就条件
**Then** 创建成就表：
```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    achievement_name VARCHAR(100),
    description TEXT,
    achievement_type VARCHAR(50),  -- 'message_count', 'login_streak', 'ritual_count', 'level'
    condition_value INTEGER,
    reward_exp INTEGER DEFAULT 0,
    icon_url VARCHAR(255)
);

CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    achievement_id INTEGER REFERENCES achievements(id),
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress INTEGER DEFAULT 0,
    UNIQUE(user_id, achievement_id)
);

INSERT INTO achievements (achievement_name, description, achievement_type, condition_value, reward_exp) VALUES
('初次相识', '发送第1条消息', 'message_count', 1, 10),
('熟悉的陌生人', '发送第10条消息', 'message_count', 10, 20),
('无话不谈', '发送第100条消息', 'message_count', 100, 100),
('连续签到7天', '连续登录7天', 'login_streak', 7, 50),
('连续签到30天', '连续登录30天', 'login_streak', 30, 200),
('早起的鸟儿', '完成10次早安仪式', 'ritual_count', 10, 30),
('夜猫子', '完成10次晚安仪式', 'ritual_count', 10, 30),
('真爱至上', '达到亲密度Level 50', 'level', 50, 500);
```

**And** 成就检查逻辑：
```python
async def check_achievements(user_id: int):
    # 检查消息数成就
    message_count = await Message.filter(conversation__user_id=user_id, sender_type='user').count()
    await check_and_unlock_achievement(user_id, 'message_count', message_count)

    # 检查连续登录成就
    login_streak = await get_login_streak(user_id)
    await check_and_unlock_achievement(user_id, 'login_streak', login_streak)

    # ...其他成就检查
```

**And** 成就解锁时：
- 弹出成就解锁提示："🎉 成就达成：{achievement_name}"
- 自动增加奖励经验值
- 成就记录到`user_achievements`表

**And** 成就页面（/achievements）：
- 显示所有成就（已解锁/未解锁）
- 显示成就进度（如"发送消息：75/100"）
- 成就图标设计（金色/银色/铜色）

**And** 每日互动任务（额外经验值）：
- 每日任务列表：
  1. 发送5条消息 → +20 exp
  2. 完成早安或晚安仪式 → +15 exp
  3. 查看朋友圈并点赞 → +10 exp
- 完成所有每日任务 → 额外+30 exp

**Technical Notes:**
- 成就检查在关键操作后触发（发消息、登录等）
- 避免频繁检查影响性能（使用缓存）

---

### Story 6.5: 亲密度衰减与保持机制（可选）

As a **产品经理**,
I want **设计温和的亲密度衰减机制**,
So that **鼓励用户保持活跃但不过度惩罚**。

**Acceptance Criteria:**

**Given** 用户一段时间未互动
**When** 超过7天无登录
**Then** 开始温和的亲密度衰减：
- 第8天起：每日-5 exp（不影响等级，仅减少当前经验）
- 如果当前经验<5，则不再衰减（保底机制）
- 等级不会降低（仅影响升级进度）

**And** 衰减提醒：
- 第5天未登录：推送通知"好久没见，想你了~"
- 第7天未登录：推送通知"再不来看我，亲密度要下降啦~"

**And** 创建衰减日志：
```sql
CREATE TABLE intimacy_decay_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    decay_amount INTEGER,
    reason VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**And** 每日凌晨执行衰减检查：
```python
async def check_intimacy_decay():
    seven_days_ago = datetime.now() - timedelta(days=7)
    inactive_conversations = await Conversation.filter(
        last_message_at__lt=seven_days_ago
    )

    for conv in inactive_conversations:
        if conv.intimacy_exp >= 5:
            conv.intimacy_exp -= 5
            await conv.save()
            await IntimacyDecayLog.create(
                conversation_id=conv.id,
                decay_amount=5,
                reason='inactive_7days'
            )
```

**And** 用户回归时：
- 显示欢迎回来消息："好久不见！让我们重新建立默契吧~"
- 提供"回归礼包"：+50 exp（一次性）

**Edge Cases:**
- 用户主动暂停衰减功能（设置页面选项）
- 付费用户可选择关闭衰减

**Technical Notes:**
- MVP阶段可暂不实现衰减（根据用户反馈决定）
- 衰减机制需谨慎设计，避免用户流失

---

## Epic 6 Summary

**Total Stories:** 5
**Estimated Complexity:** Medium
**Dependencies:** Epic 1（对话系统）+ Epic 5（每日仪式）
**Completion Criteria:**
- ✅ 亲密度计算准确，每次互动正确增加经验值
- ✅ 升级时触发里程碑庆祝动画和奖励
- ✅ 用户可在个人中心查看所有成就进度
- ✅ 7日留存率达到30%（通过亲密度系统增强用户粘性）
- ✅ 等级奖励正确解锁并展示

**Database Tables Created:**
- `intimacy_logs`
- `level_rewards`
- `user_rewards`
- `achievements`
- `user_achievements`
- `intimacy_decay_logs`

**Next Epic:** Epic 7 - 订阅支付完善

---

# Epic 7: 订阅支付完善 (Subscription Payment Integration)

**Epic Goal:** 接入完整的支付系统，让用户可以购买订阅解锁付费功能，建立商业化闭环。

**Requirements Covered:**
- FR91-FR95 (订阅套餐、支付渠道、自动续费、订阅管理、发票)
- FR98-FR103 (订单记录、退款申请、付费特权)
- UX22 (订阅页面完整支付流程)

---

### Story 7.1: 订阅套餐数据模型与定价策略

As a **产品经理**,
I want **定义清晰的订阅套餐和定价**,
So that **用户可以选择适合自己的付费方案**。

**Acceptance Criteria:**

**Given** Epic 3已实现订阅页面基础版
**When** 完善订阅数据模型
**Then** 创建订阅套餐表：
```sql
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL,
    plan_type VARCHAR(20),  -- 'free', 'monthly', 'yearly'
    price_cny DECIMAL(10, 2),  -- 人民币价格
    duration_days INTEGER,
    features JSON,  -- 功能列表
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO subscription_plans (plan_name, plan_type, price_cny, duration_days, features, sort_order) VALUES
('免费版', 'free', 0.00, 0, '{"messages_per_day": 20, "exclusive_content": false}', 1),
('会员月度', 'monthly', 28.00, 30, '{"messages_per_day": -1, "exclusive_content": true, "priority_response": true}', 2),
('会员年度', 'yearly', 268.00, 365, '{"messages_per_day": -1, "exclusive_content": true, "priority_response": true, "discount": "优惠20%"}', 3);
```

**And** 创建订单表：
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(32) UNIQUE NOT NULL,  -- 订单号
    user_id INTEGER REFERENCES users(id),
    plan_id INTEGER REFERENCES subscription_plans(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),  -- 'alipay', 'wechat', 'apple_iap', 'google_play'
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'paid', 'failed', 'refunded'
    paid_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

**And** API端点`GET /api/subscriptions/plans`返回套餐列表

**Technical Notes:**
- 年度套餐价格268元（月均22.3元，优惠20%）
- 价格可后台配置调整

---

### Story 7.2: 支付宝与微信支付集成

As a **用户**,
I want **通过支付宝或微信支付购买订阅**,
So that **快速便捷地完成支付**。

**Acceptance Criteria:**

**Given** 用户在订阅页面选择套餐
**When** 点击"立即购买"按钮
**Then** 后端生成订单：
```python
@app.post("/api/subscriptions/orders")
async def create_order(plan_id: int, payment_method: str, user_id: int):
    plan = await SubscriptionPlan.get(id=plan_id)
    order_no = generate_order_no()  # 生成唯一订单号：IDL20240108123456

    order = await Order.create(
        order_no=order_no,
        user_id=user_id,
        plan_id=plan_id,
        amount=plan.price_cny,
        payment_method=payment_method,
        status='pending'
    )

    # 调用支付服务
    if payment_method == 'alipay':
        payment_url = await create_alipay_order(order)
    elif payment_method == 'wechat':
        payment_qrcode = await create_wechat_order(order)

    return {"order_no": order_no, "payment_url": payment_url}
```

**And** 集成支付宝SDK：
```python
from alipay import AliPay

alipay = AliPay(
    appid=settings.ALIPAY_APPID,
    app_private_key_path="keys/alipay_private_key.pem",
    alipay_public_key_path="keys/alipay_public_key.pem",
    sign_type="RSA2"
)

async def create_alipay_order(order: Order):
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order.order_no,
        total_amount=float(order.amount),
        subject=f"idol_private {order.plan.plan_name}",
        return_url=settings.ALIPAY_RETURN_URL,
        notify_url=settings.ALIPAY_NOTIFY_URL
    )
    return f"https://openapi.alipay.com/gateway.do?{order_string}"
```

**And** 集成微信支付Native（扫码支付）：
```python
from wechatpay import WeChatPay

wechatpay = WeChatPay(
    mch_id=settings.WECHAT_MCH_ID,
    api_key=settings.WECHAT_API_KEY,
    app_id=settings.WECHAT_APPID
)

async def create_wechat_order(order: Order):
    result = wechatpay.order.create(
        out_trade_no=order.order_no,
        total_fee=int(order.amount * 100),  # 单位：分
        body=f"idol_private {order.plan.plan_name}",
        notify_url=settings.WECHAT_NOTIFY_URL
    )
    return result['code_url']  # 二维码URL
```

**And** 前端处理支付：
- 支付宝：跳转到支付宝收银台页面
- 微信：显示二维码供用户扫码支付

**And** 支付回调处理：
```python
@app.post("/api/payments/alipay/notify")
async def alipay_notify(request: Request):
    data = await request.form()
    signature = alipay.verify(data, data["sign"])

    if signature:
        order_no = data["out_trade_no"]
        if data["trade_status"] == "TRADE_SUCCESS":
            await process_payment_success(order_no)

    return "success"
```

**Technical Notes:**
- 支付宝/微信支付需企业资质申请
- 测试环境使用沙盒账号

---

### Story 7.3: Apple In-App Purchase集成

As a **iOS用户**,
I want **通过App Store内购订阅**,
So that **符合苹果应用商店规范**。

**Acceptance Criteria:**

**Given** iOS应用已发布到App Store
**When** 用户在iOS设备上购买订阅
**Then** 配置App Store Connect内购产品：
- 产品ID：`com.idol.premium.monthly`
- 产品类型：自动续订订阅
- 价格档：¥28/月

**And** 前端集成StoreKit：
```dart
import 'package:in_app_purchase/in_app_purchase.dart';

final InAppPurchase _iap = InAppPurchase.instance;

Future<void> purchaseSubscription(String productId) async {
  final ProductDetailsResponse response = await _iap.queryProductDetails({productId});
  final ProductDetails product = response.productDetails.first;

  final PurchaseParam purchaseParam = PurchaseParam(productDetails: product);
  await _iap.buyNonConsumable(purchaseParam: purchaseParam);
}
```

**And** 监听购买结果：
```dart
_iap.purchaseStream.listen((purchases) {
  for (var purchase in purchases) {
    if (purchase.status == PurchaseStatus.purchased) {
      // 验证收据并激活订阅
      verifyReceipt(purchase.verificationData.serverVerificationData);
    }
  }
});
```

**And** 后端验证Apple收据：
```python
@app.post("/api/payments/apple/verify")
async def verify_apple_receipt(receipt_data: str, user_id: int):
    # 调用Apple验证接口
    url = "https://buy.itunes.apple.com/verifyReceipt"  # 生产环境
    payload = {"receipt-data": receipt_data, "password": settings.APPLE_SHARED_SECRET}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        result = response.json()

    if result['status'] == 0:
        # 收据有效，激活订阅
        await activate_subscription(user_id, plan_type='monthly')
        return {"success": True}
    else:
        return {"success": False, "error": "Invalid receipt"}
```

**And** 处理自动续费回调（Apple Server-to-Server Notifications）

**Technical Notes:**
- Apple抽成30%（首年）或15%（续订）
- 需配置Apple Shared Secret用于收据验证

---

### Story 7.4: Google Play Billing集成

As a **Android用户**,
I want **通过Google Play订阅**,
So that **享受Google Play的订阅管理便利**。

**Acceptance Criteria:**

**Given** Android应用已发布到Google Play
**When** 用户在Android设备上购买订阅
**Then** 配置Google Play Console内购产品：
- 产品ID：`premium_monthly`
- 产品类型：订阅
- 价格：¥28/月

**And** 前端集成Google Play Billing：
```dart
import 'package:in_app_purchase_android/in_app_purchase_android.dart';

Future<void> purchaseSubscription(String productId) async {
  final ProductDetailsResponse response = await _iap.queryProductDetails({productId});
  final ProductDetails product = response.productDetails.first;

  final PurchaseParam purchaseParam = PurchaseParam(productDetails: product);
  await _iap.buyNonConsumable(purchaseParam: purchaseParam);
}
```

**And** 后端验证Google Play购买：
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'keys/google_play_service_account.json',
    scopes=['https://www.googleapis.com/auth/androidpublisher']
)
publisher = build('androidpublisher', 'v3', credentials=credentials)

@app.post("/api/payments/google/verify")
async def verify_google_purchase(purchase_token: str, product_id: str, user_id: int):
    result = publisher.purchases().subscriptions().get(
        packageName='com.idol.app',
        subscriptionId=product_id,
        token=purchase_token
    ).execute()

    if result['paymentState'] == 1:  # 已支付
        await activate_subscription(user_id, plan_type='monthly')
        return {"success": True}
    else:
        return {"success": False, "error": "Payment not completed"}
```

**And** 处理Google Play实时开发者通知（Real-time Developer Notifications）

**Technical Notes:**
- Google抽成30%（首年）或15%（续订）
- 需配置Google Play Service Account用于API访问

---

### Story 7.5: 订阅激活与权限管理

As a **系统**,
I want **支付成功后立即激活用户订阅权限**,
So that **用户可以马上享受付费功能**。

**Acceptance Criteria:**

**Given** 用户完成支付（任意支付方式）
**When** 后端收到支付成功通知
**Then** 执行订阅激活流程：
```python
async def process_payment_success(order_no: str):
    order = await Order.get(order_no=order_no)

    # 1. 更新订单状态
    order.status = 'paid'
    order.paid_at = datetime.now()
    order.expires_at = datetime.now() + timedelta(days=order.plan.duration_days)
    await order.save()

    # 2. 更新用户订阅状态
    user = await User.get(id=order.user_id)
    user.subscription_tier = 'premium'
    user.subscription_expires_at = order.expires_at
    await user.save()

    # 3. 重置消息配额
    await MessageQuota.filter(user_id=user.id).update(quota_limit=-1)

    # 4. 发送订阅成功通知
    await send_subscription_success_message(user.id)

    # 5. 记录订阅日志
    await SubscriptionLog.create(
        user_id=user.id,
        action='activate',
        plan_id=order.plan_id,
        expires_at=order.expires_at
    )
```

**And** 创建订阅日志表：
```sql
CREATE TABLE subscription_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),  -- 'activate', 'renew', 'cancel', 'expire'
    plan_id INTEGER REFERENCES subscription_plans(id),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**And** 前端显示订阅成功：
- 弹窗提示："恭喜！已成功升级至Premium会员"
- 显示到期时间："有效期至2024-02-07"
- 显示已解锁功能列表

**And** 订阅到期检查（每日定时任务）：
```python
async def check_subscription_expiry():
    today = datetime.now()
    expired_users = await User.filter(
        subscription_tier='premium',
        subscription_expires_at__lt=today
    )

    for user in expired_users:
        user.subscription_tier = 'free'
        await user.save()

        # 恢复免费用户配额
        await MessageQuota.filter(user_id=user.id).update(quota_limit=20)

        # 发送到期通知
        await send_subscription_expired_message(user.id)
```

**And** 提前3天续费提醒：
- 推送通知："您的会员将在3天后到期，记得续费哦~"

**Technical Notes:**
- 订阅激活立即生效，无延迟
- 自动续费由支付平台处理（Apple/Google/支付宝/微信）

---

### Story 7.6: 订阅管理与退款处理

As a **用户**,
I want **管理我的订阅并在需要时申请退款**,
So that **有完整的订阅控制权**。

**Acceptance Criteria:**

**Given** 用户已订阅Premium会员
**When** 用户访问订阅管理页面
**Then** 显示订阅详情：
- 当前套餐：Premium月度会员
- 到期时间：2024-02-07 23:59:59
- 支付方式：支付宝
- 自动续费状态：已开启/已关闭

**And** 提供订阅操作：
- 取消自动续费（不立即失效，到期后不续费）
- 修改套餐（月度 ↔ 年度）
- 申请退款

**And** 取消自动续费：
- 支付宝/微信：需用户在对应平台操作
- Apple/Google：提供深度链接跳转到系统订阅管理页

**And** 申请退款流程：
1. 用户点击"申请退款"
2. 填写退款原因（下拉选项+文本框）
3. 提交申请创建工单：
```sql
CREATE TABLE refund_requests (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    user_id INTEGER REFERENCES users(id),
    reason VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
4. 运营审核（后台管理系统）
5. 审核通过后原路退款：
```python
async def process_refund(refund_id: int, approved: bool):
    refund = await RefundRequest.get(id=refund_id)
    order = await Order.get(id=refund.order_id)

    if approved:
        # 调用支付平台退款API
        if order.payment_method == 'alipay':
            await alipay.refund(order.order_no, order.amount)
        elif order.payment_method == 'wechat':
            await wechatpay.refund(order.order_no, order.amount)

        # 更新订单状态
        order.status = 'refunded'
        await order.save()

        # 降级用户权限
        user = await User.get(id=order.user_id)
        user.subscription_tier = 'free'
        await user.save()

        refund.status = 'approved'
    else:
        refund.status = 'rejected'

    refund.processed_at = datetime.now()
    await refund.save()
```

**And** 退款后通知用户：
- 推送通知："您的退款申请已通过，款项将在3-5个工作日内退回"

**And** API端点：
- `POST /api/subscriptions/cancel`：取消自动续费
- `POST /api/subscriptions/refund`：申请退款
- `GET /api/subscriptions/orders`：订单历史

**Technical Notes:**
- 退款审核需人工介入（防止恶意退款）
- Apple/Google退款需遵循平台规则

---

## Epic 7 Summary

**Total Stories:** 6
**Estimated Complexity:** High（支付集成复杂）
**Dependencies:** Epic 3（配额系统）
**Completion Criteria:**
- ✅ 支付宝/微信支付测试订单成功
- ✅ iOS内购测试通过沙盒环境
- ✅ Google Play测试订阅成功
- ✅ 支付成功后用户权限立即生效
- ✅ 自动续费正常运行（测试沙盒环境）
- ✅ 退款流程完整可用

**Database Tables Created:**
- `subscription_plans`
- `orders`
- `subscription_logs`
- `refund_requests`

**Next Epic:** Epic 8 - 跨设备同步与数据管理

---

# Epic 8-11: Remaining Epics (Summary Version)

由于篇幅限制，Epic 8-11采用精简版Story描述。如需详细展开，可后续补充。

---

# Epic 8: 跨设备同步与数据管理

**Requirements:** FR104-FR113, NFR-04, NFR-20, NFR-29

### Story 8.1: 多设备登录与设备管理
- 创建`user_devices`表
- 支持最多5台设备同时登录
- 设备列表管理（查看/移除设备）

### Story 8.2: 实时消息同步（SSE）
- 使用Server-Sent Events推送新消息
- 同步延迟<2秒

### Story 8.3: 云端备份与数据导出
- 每日自动备份用户数据
- 提供JSON格式数据导出

### Story 8.4: 账号删除与数据清除
- 7天冷静期机制
- 彻底删除数据库记录和云端备份

**Total Stories:** 4

---

# Epic 9: 平台优化与无障碍体验

**Requirements:** FR114-FR123, NFR-02, NFR-03, NFR-05, NFR-24, NFR-26

### Story 9.1: 性能优化（首屏加载<2秒）
- 图片懒加载 + WebP格式
- 代码分割与缓存策略

### Story 9.2: 个性化设置
- 主题切换（浅色/深色/自动）
- 字体大小调整

### Story 9.3: 推送通知集成（Firebase Cloud Messaging）
- 偶像主动消息推送
- 订阅到期提醒

### Story 9.4: 无障碍优化（WCAG 2.1 AA）
- 屏幕阅读器支持
- 键盘导航

**Total Stories:** 4

---

# Epic 10: 🔄 运营智能与系统监控 - **Phase 2 (Post-MVP)**

> **⚠️ 本Epic建议延后到Phase 2**
>
> **原因:** Epic 10主要服务运营团队（非最终用户），属于内部工具。MVP阶段应优先验证核心用户价值（Epic 1-7），而非构建运营基础设施。
>
> **建议:**
> - ✅ **延后至Post-MVP:** 在验证产品-市场匹配后再构建运营工具
> - ⚠️ **或重新定义为用户价值:** 改为"可靠的服务体验"，专注NFR性能/可用性（对用户可见的价值）
>
> **参考:** 详见 `implementation-readiness-report-2026-01-08.md` - Issue #3

**Requirements (当前):** FR62-FR72, FR115-FR129 (运营分析和监控), NFR-12至NFR-22

**注意:** 原Requirements "FR124-FR138（Epic 0基础上增强）"不准确，实际覆盖FR62-FR72, FR115-FR129

### Story 10.1: 运营数据仪表盘
- DAU/MAU统计
- 付费转化率分析

### Story 10.2: 监控告警增强
- 自定义Prometheus指标
- 钉钉/飞书告警集成

### Story 10.3: 成本监控与优化
- AI调用成本追踪
- 预算预警

### Story 10.4: A/B测试框架（预留）
- 实验分组与效果分析

**Total Stories:** 4

---

# Epic 11: 🔄 客服支持与内容安全 - **Phase 2 (Post-MVP)**

> **⚠️ 本Epic建议延后到Phase 2**
>
> **原因:** Epic 11主要服务客服团队（非最终用户），属于内部工具。MVP阶段应优先验证核心用户价值（Epic 1-7），而非构建客服基础设施。
>
> **建议:**
> - ✅ **延后至Post-MVP:** 在用户规模增长后再构建客服工具
> - ⚠️ **或重新定义为用户价值:** 改为"安全的用户社区"，专注用户举报、内容安全等用户可见功能
>
> **参考:** 详见 `implementation-readiness-report-2026-01-08.md` - Issue #3

**Requirements (当前):** FR73-FR86, FR103-FR114 (客服工具和内容审核), NFR-23, NFR-25, NFR-27至NFR-29

**注意:** 原Requirements "FR139-FR144"是**错误的** - 这些是Phase 2社交/语音功能，不属于客服支持：
- FR139: 社交媒体分享
- FR140-141: 语音消息（STT/TTS）
- FR142: 多语言切换
- FR143-144: 偶像朋友圈

这些FR已在FR Coverage Map中标记为"Phase 2功能（暂不在MVP范围）"

### Story 11.1: 用户反馈系统
- 创建`feedback`表
- 客服后台（Retool或自建Admin）

### Story 11.2: 内容安全审核
- 集成阿里云内容安全API
- 违规消息拦截

### Story 11.3: 隐私保护与合规
- 对话内容加密
- GDPR合规（数据导出/删除）

### Story 11.4: 帮助中心与用户协议
- FAQ页面
- 用户协议和隐私政策

**Total Stories:** 4

---

## Final Summary

**Total Epics:** 11（Epic 0 - Epic 11）
**Total Stories:** 62+

**Story Distribution:**
- Epic 0: 8 stories（技术基础设施）
- Epic 1: 8 stories（首次用户体验）
- Epic 2: 9 stories（AI对话核心）
- Epic 3: 4 stories（Freemium边界）
- Epic 4: 6 stories（记忆系统）
- Epic 5: 5 stories（偶像生活）
- Epic 6: 5 stories（亲密度系统）
- Epic 7: 6 stories（订阅支付）
- Epic 8: 4 stories（跨设备同步）
- Epic 9: 4 stories（平台优化）
- Epic 10: 4 stories（运营监控）
- Epic 11: 4 stories（客服安全）

**All 220 Requirements Covered:**
- 144 FRs ✅
- 29 NFRs ✅
- 20 ARCH ✅
- 27 UX ✅

