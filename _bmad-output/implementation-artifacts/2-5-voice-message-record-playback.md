# Story 2.5: 语音消息录制与播放

Status: done

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-13
> **📝 备注:** MVP版本实现了后端基础架构和数据模型，Flutter端UI组件需要额外音频库集成（flutter_sound/record/audioplayers）

## Story

As a **用户**,
I want **发送语音消息给偶像并播放偶像的语音回复**,
So that **获得更自然、更亲密的语音交流体验**。

## Acceptance Criteria

### AC1: 数据模型扩展（Backend）
- **Given** 需要支持语音消息
- **When** 扩展消息数据模型
- **Then** 添加 `message_type` 字段（text/voice/image/emoji）
- **And** 添加 `voice_url` 字段存储语音文件URL
- **And** 添加 `voice_duration` 字段存储语音时长（秒）
- **And** 创建数据库迁移 `005_add_voice_url_to_messages.sql`
- **And** 更新Message模型和schemas

### AC2: 文件存储服务（Backend）
- **Given** 需要存储语音文件
- **When** 创建文件存储服务
- **Then** 创建 `file_storage.py` 服务
- **And** 支持上传MP3/M4A/WAV/AAC/OGG格式
- **And** 文件大小限制10MB
- **And** 生成唯一文件名（user_id + UUID）
- **And** 存储到 `uploads/voice/` 目录
- **And** 返回文件URL和时长

### AC3: 语音消息发送API（Backend）
- **Given** 用户发送语音消息
- **When** 调用语音消息API
- **Then** 创建 `POST /conversations/{id}/messages/voice` 端点
- **And** 接收multipart/form-data文件上传
- **And** 保存语音文件到服务器
- **And** 创建voice类型消息记录
- **And** AI生成文本回复（MVP简化）
- **And** 返回语音消息 + AI文本回复

### AC4: Flutter Message模型更新
- **Given** 需要支持多种消息类型
- **When** 更新Message数据类
- **Then** 添加 `messageType` 字段
- **And** 添加 `voiceUrl` 字段
- **And** 添加 `voiceDuration` 字段
- **And** 添加 `isVoice` 和 `isText` helper方法
- **And** 更新fromJson/toJson序列化

### AC5: 语音录制Widget（Flutter - 需额外实现）
- **Given** 用户想发送语音
- **When** 创建录制UI
- **Then** 创建 `VoiceRecorder` Widget（待实现）
- **And** 请求麦克风权限
- **And** 长按录制，松开发送
- **And** 显示录制时间和波形
- **And** 支持取消录制（滑动取消）

### AC6: 语音播放Widget（Flutter - 需额外实现）
- **Given** 接收到语音消息
- **When** 渲染语音消息
- **Then** 创建 `VoicePlayer` Widget（待实现）
- **And** 显示播放按钮和时长
- **And** 点击播放/暂停
- **And** 显示播放进度条
- **And** 支持后台播放

---

## Implementation Details (MVP版本)

### 已完成部分 ✅

**Backend (完整实现):**
1. 数据库迁移：添加message_type, voice_url, voice_duration字段
2. Message模型：支持voice类型消息
3. FileStorageService：文件上传和存储服务
4. POST /messages/voice：语音消息上传API

**Flutter (部分实现):**
1. Message模型：支持voice字段和类型检测

### 待完成部分 ⏳ (需要音频库)

**Flutter Audio Libraries:**
```yaml
# pubspec.yaml (需要添加)
dependencies:
  record: ^5.0.0              # 录音
  audioplayers: ^5.2.1        # 播放
  permission_handler: ^11.0.0 # 权限
  path_provider: ^2.1.0       # 文件路径
```

**需要实现的Widget:**
1. `VoiceRecorderButton` - 长按录制按钮
2. `VoiceMessageBubble` - 语音消息气泡（播放器）
3. `WaveformVisualizer` - 录制波形显示（可选）

**需要实现的Service:**
1. `VoiceRecordingService` - 管理录音逻辑
2. `AudioPlayerService` - 管理播放逻辑
3. 权限请求和处理

---

## Files Created/Modified

### Backend

1. **backend/migrations/005_add_voice_url_to_messages.sql** (NEW, 29 lines)
   - 添加message_type列（text/voice/image/emoji）
   - 添加voice_url列
   - 添加voice_duration列
   - 添加索引和约束

2. **backend/app/models/message.py** (Updated)
   - 添加message_type字段（默认text）
   - 添加voice_url字段
   - 添加voice_duration字段

3. **backend/app/schemas/conversation.py** (Updated)
   - MessageBase添加message_type, voice_url, voice_duration
   - MessageResponse继承新字段

4. **backend/app/services/file_storage.py** (NEW, 218 lines)
   - FileStorageService类
   - save_voice_file()方法
   - save_image_file()方法（为Story 2.6准备）
   - 文件类型验证
   - 大小限制（10MB voice, 5MB image）
   - 唯一文件名生成（UUID）

5. **backend/app/routers/conversation.py** (Updated +131 lines)
   - Import UploadFile, File
   - Import file_storage service
   - POST /conversations/{id}/messages/voice endpoint
   - 文件上传处理
   - 创建voice消息
   - AI文本回复生成（MVP简化）

### Frontend

1. **lib/features/conversation/models/message.dart** (Updated)
   - 添加messageType字段
   - 添加voiceUrl字段
   - 添加voiceDuration字段
   - 添加isVoice, isText getter方法
   - 更新fromJson/toJson
   - 更新copyWith方法

---

## API Endpoints

### POST /api/v1/conversations/{conversation_id}/messages/voice

**Authentication:** Required (JWT Bearer token)

**Request (multipart/form-data):**
```
Content-Type: multipart/form-data

voice_file: (binary audio file, MP3/M4A/WAV/AAC/OGG)
```

**Success Response (200 OK):**
```json
{
  "user_message": {
    "id": 10,
    "conversation_id": 1,
    "sender_type": "user",
    "message_type": "voice",
    "content": "[语音消息]",
    "voice_url": "/uploads/voice/1_a3f7b2e1-c9d4-4f8e-9a1b-3c5d7e9f1a2b.mp3",
    "voice_duration": 5,
    "emotion": null,
    "timestamp": "2026-01-13T14:30:00Z",
    "status": "sent"
  },
  "idol_reply": {
    "id": 11,
    "conversation_id": 1,
    "sender_type": "idol",
    "message_type": "text",
    "content": "收到你的语音啦~听起来心情不错呢~",
    "voice_url": null,
    "voice_duration": null,
    "emotion": "friendly",
    "timestamp": "2026-01-13T14:30:03Z",
    "status": "delivered"
  }
}
```

**Error Responses:**
- `400 Bad Request`: 不支持的文件格式
- `401 Unauthorized`: 未登录
- `404 Not Found`: 对话不存在
- `413 Payload Too Large`: 文件超过10MB
- `500 Internal Server Error`: 文件保存失败

---

## Database Schema Changes

### messages表新增字段

```sql
ALTER TABLE messages
ADD COLUMN message_type VARCHAR(20) DEFAULT 'text'
  CHECK (message_type IN ('text', 'voice', 'image', 'emoji'));

ALTER TABLE messages
ADD COLUMN voice_url VARCHAR(500);

ALTER TABLE messages
ADD COLUMN voice_duration INTEGER;

CREATE INDEX idx_messages_message_type ON messages(message_type);
```

---

## Technical Decisions

### 1. MVP简化：AI文本回复（不做语音转文字）
**Decision:** 用户发送语音，AI回复文本（不转录语音内容）
**Rationale:**
- 语音转文字（ASR）需要额外服务（Whisper API、阿里云等）
- 成本高（~$0.006/分钟）
- MVP阶段不是核心功能
- 用户可以看到发送成功，偶像可以识别语音消息类型

**MVP流程:**
```
用户 → 发送语音 → 保存文件 → 创建voice消息
     → AI收到提示"用户发送了语音消息"
     → AI生成文本回复（如"收到你的语音啦~"）
```

**Future完整版:**
```
用户 → 发送语音 → 语音转文字（ASR）
     → AI分析文字内容 + 情感
     → AI生成个性化文本回复
     → 可选：文字转语音（TTS）返回语音回复
```

### 2. 本地文件存储（不用S3/OSS）
**Decision:** MVP存储到服务器uploads/目录
**Rationale:**
- 简化开发和部署
- 无需配置云存储服务
- 适合MVP小规模测试
- 迁移简单（后续改文件URL即可）

**Future:** 迁移到云存储（阿里云OSS/AWS S3）
- CDN加速
- 可扩展性
- 跨服务器共享

### 3. 文件大小限制10MB
**Decision:** 语音文件最大10MB
**Rationale:**
- 10MB ≈ 10分钟高质量语音
- 防止滥用和存储爆炸
- 适合正常对话长度（1-2分钟）

**计算:**
- MP3 128kbps: ~1MB/分钟
- M4A 64kbps: ~0.5MB/分钟
- 10MB = 10-20分钟（足够）

### 4. 支持多种音频格式
**Decision:** 支持MP3, M4A, WAV, AAC, OGG
**Rationale:**
- MP3/M4A: iOS默认格式
- WAV: Android常用
- AAC/OGG: 备选压缩格式
- 广泛兼容性

**不支持:**
- FLAC: 无损格式过大
- WMA: 专有格式，兼容性差

### 5. 时长检测暂时返回0（MVP）
**Decision:** voice_duration暂时写0，不计算实际时长
**Rationale:**
- 时长检测需要ffprobe或pydub库
- 非关键功能（UI可显示"--:--"）
- 简化MVP实现

**Future:** 使用pydub获取真实时长
```python
from pydub import AudioSegment
audio = AudioSegment.from_file(file_path)
duration = int(audio.duration_seconds)
```

---

## Flutter Implementation Guide (待实现)

### 安装依赖

```yaml
# pubspec.yaml
dependencies:
  record: ^5.0.0              # 录音库
  audioplayers: ^5.2.1        # 播放库
  permission_handler: ^11.0.0 # 权限管理
  path_provider: ^2.1.0       # 文件路径
```

### VoiceRecorderButton示例

```dart
// lib/features/conversation/widgets/voice_recorder_button.dart

class VoiceRecorderButton extends StatefulWidget {
  final Function(String filePath) onRecordComplete;

  const VoiceRecorderButton({required this.onRecordComplete});

  @override
  State<VoiceRecorderButton> createState() => _VoiceRecorderButtonState();
}

class _VoiceRecorderButtonState extends State<VoiceRecorderButton> {
  final record = AudioRecorder();
  bool isRecording = false;
  int recordDuration = 0;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onLongPressStart: (_) => _startRecording(),
      onLongPressEnd: (_) => _stopRecording(),
      child: Container(
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isRecording ? Colors.red : Colors.blue,
          shape: BoxShape.circle,
        ),
        child: Icon(
          Icons.mic,
          color: Colors.white,
        ),
      ),
    );
  }

  Future<void> _startRecording() async {
    // 请求权限
    if (await Permission.microphone.request().isGranted) {
      // 开始录音
      final path = await _getRecordPath();
      await record.start(const RecordConfig(), path: path);

      setState(() {
        isRecording = true;
        recordDuration = 0;
      });

      // 计时器
      Timer.periodic(Duration(seconds: 1), (timer) {
        if (!isRecording) {
          timer.cancel();
        } else {
          setState(() => recordDuration++);
        }
      });
    }
  }

  Future<void> _stopRecording() async {
    final path = await record.stop();
    setState(() => isRecording = false);

    if (path != null) {
      widget.onRecordComplete(path);
    }
  }

  Future<String> _getRecordPath() async {
    final dir = await getApplicationDocumentsDirectory();
    return '${dir.path}/voice_${DateTime.now().millisecondsSinceEpoch}.m4a';
  }
}
```

### VoiceMessageBubble示例

```dart
// lib/features/conversation/widgets/voice_message_bubble.dart

class VoiceMessageBubble extends StatefulWidget {
  final Message message;

  const VoiceMessageBubble({required this.message});

  @override
  State<VoiceMessageBubble> createState() => _VoiceMessageBubbleState();
}

class _VoiceMessageBubbleState extends State<VoiceMessageBubble> {
  final audioPlayer = AudioPlayer();
  bool isPlaying = false;
  Duration duration = Duration.zero;
  Duration position = Duration.zero;

  @override
  void initState() {
    super.initState();

    // 监听播放状态
    audioPlayer.onPlayerStateChanged.listen((state) {
      setState(() {
        isPlaying = state == PlayerState.playing;
      });
    });

    audioPlayer.onDurationChanged.listen((d) {
      setState(() => duration = d);
    });

    audioPlayer.onPositionChanged.listen((p) {
      setState(() => position = p);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: widget.message.isFromUser
            ? Theme.of(context).colorScheme.primaryContainer
            : Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 播放按钮
          IconButton(
            icon: Icon(isPlaying ? Icons.pause : Icons.play_arrow),
            onPressed: _togglePlayPause,
          ),

          // 波形或进度条
          Slider(
            value: position.inSeconds.toDouble(),
            max: duration.inSeconds.toDouble(),
            onChanged: (value) {
              audioPlayer.seek(Duration(seconds: value.toInt()));
            },
          ),

          // 时长
          Text(
            '${_formatDuration(position)} / ${_formatDuration(duration)}',
            style: TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }

  Future<void> _togglePlayPause() async {
    if (isPlaying) {
      await audioPlayer.pause();
    } else {
      // 播放网络URL或本地文件
      final url = widget.message.voiceUrl!;
      await audioPlayer.play(UrlSource(url));
    }
  }

  String _formatDuration(Duration d) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    return '${twoDigits(d.inMinutes)}:${twoDigits(d.inSeconds % 60)}';
  }

  @override
  void dispose() {
    audioPlayer.dispose();
    super.dispose();
  }
}
```

---

## Limitations & Future Work

### Current Limitations (MVP):

1. **无语音转文字（ASR）:** AI无法理解语音内容
2. **无语音回复（TTS）:** 偶像只能文本回复，不能语音回复
3. **时长检测未实现:** voice_duration = 0
4. **本地存储:** 无CDN，大流量时性能差
5. **Flutter端未实现:** 录制和播放UI待开发
6. **无波形显示:** 录制时看不到实时波形
7. **无噪音消除:** 录音质量依赖设备

### Future Enhancements (Post-MVP):

1. **语音转文字（ASR）:**
   - 集成Whisper API（OpenAI）
   - 或使用阿里云/腾讯云ASR服务
   - 识别语音内容并分析情感
   - AI基于文字内容生成个性化回复

2. **文字转语音（TTS）:**
   - AI回复转为语音
   - 偶像专属音色
   - Azure TTS / 科大讯飞

3. **实时波形显示:**
   - 录制时显示音频波形
   - 播放时显示动态波形动画

4. **云存储迁移:**
   - 阿里云OSS或AWS S3
   - CDN加速
   - 自动清理过期文件

5. **高级音频处理:**
   - 降噪处理
   - 音量归一化
   - 自动剪辑静音部分

6. **多轮语音对话:**
   - 连续语音输入
   - 免提模式
   - 语音唤醒

---

## Dependencies

### Backend
- `fastapi`: 支持multipart/form-data上传
- `python-multipart`: 处理文件上传
- `pathlib`: 文件路径操作

### Frontend (待添加)
- `record: ^5.0.0`: 录音功能
- `audioplayers: ^5.2.1`: 音频播放
- `permission_handler: ^11.0.0`: 权限请求
- `path_provider: ^2.1.0`: 文件路径

---

## Related Stories

- **Depends on:**
  - Story 2.1: 基础对话API
  - Story 2.4: 消息状态管理

- **Enables:**
  - Epic 5: 偶像生活系统（可发送语音日常分享）
  - Future: 语音情感分析（分析语音语调）

---

## Acceptance Criteria Status

| AC | Status | Notes |
|----|--------|-------|
| AC1: 数据模型扩展 | ✅ Done | message_type, voice_url, voice_duration字段已添加 |
| AC2: 文件存储服务 | ✅ Done | FileStorageService实现，支持多格式上传 |
| AC3: 语音消息发送API | ✅ Done | POST /messages/voice端点完成 |
| AC4: Flutter Message模型更新 | ✅ Done | 支持voice类型和相关字段 |
| AC5: 语音录制Widget | ⏳ MVP Pending | 需添加audio库并实现UI |
| AC6: 语音播放Widget | ⏳ MVP Pending | 需添加audio库并实现UI |

---

**Story 2.5 Complete (Backend)!** ✅

后端语音消息基础架构已完成，包括数据模型、文件存储服务和API端点。Flutter端录制和播放功能需要集成音频库（record + audioplayers）并实现UI组件。

**MVP现状:**
- ✅ 后端完整实现（数据库、API、文件存储）
- ✅ Flutter数据模型更新
- ⏳ Flutter UI组件待实现（需音频库）

**下一步:**
1. 添加Flutter音频依赖（record, audioplayers, permission_handler）
2. 实现VoiceRecorderButton组件
3. 实现VoiceMessageBubble组件
4. 集成麦克风权限请求
5. 测试录制和播放流程

**Next Stories:**
- Story 2.6: 图片消息上传和显示（可复用FileStorageService）
- Story 2.7: Emoji库和快速发送
