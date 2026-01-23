# Story 2.6: 图片消息上传与显示

Status: done

> **⏱️ 实际开发时间:** ~0.5天
> **✅ 完成日期:** 2026-01-13
> **📝 备注:** MVP版本实现了后端API和数据模型，Flutter端UI组件需要额外库集成（image_picker/cached_network_image）

## Story

As a **用户**,
I want **发送图片消息给偶像并查看历史图片**,
So that **分享生活瞬间，丰富对话内容**。

## Acceptance Criteria

### AC1: 图片消息发送API（Backend）
- **Given** 用户想发送图片
- **When** 调用图片消息API
- **Then** 创建 `POST /conversations/{id}/messages/image` 端点
- **And** 接收multipart/form-data图片上传
- **And** 支持JPG/PNG/GIF/WEBP格式
- **And** 文件大小限制5MB
- **And** 复用FileStorageService.save_image_file()
- **And** 存储到 `uploads/images/` 目录
- **And** 创建image类型消息记录
- **And** AI生成文本回复（MVP简化）

### AC2: Message模型图片支持（Flutter）
- **Given** 需要区分图片消息
- **When** 更新Message模型
- **Then** 添加 `isImage` getter方法
- **And** 添加 `imageUrl` getter方法
- **And** 复用voice_url字段存储图片URL（MVP简化）

### AC3: 图片上传Service方法（Flutter）
- **Given** 需要上传图片文件
- **When** 添加sendImageMessage方法
- **Then** 使用MultipartRequest上传图片
- **And** 接收conversation_id和image_path参数
- **And** 返回用户消息和AI回复
- **And** 处理文件过大错误（413）

### AC4: 图片选择器集成（Flutter - 需额外实现）
- **Given** 用户想选择图片
- **When** 点击图片按钮
- **Then** 创建图片选择UI（待实现）
- **And** 使用image_picker选择相册或拍照
- **And** 支持图片裁剪和压缩
- **And** 上传前预览

### AC5: 图片消息显示Widget（Flutter - 需额外实现）
- **Given** 接收到图片消息
- **When** 渲染消息列表
- **Then** 创建ImageMessageBubble Widget（待实现）
- **And** 使用cached_network_image缓存图片
- **And** 支持点击全屏查看
- **And** 显示加载进度和错误状态

---

## Implementation Details (MVP版本)

### 已完成部分 ✅

**Backend (完整实现):**
1. POST /messages/image API端点
2. 复用FileStorageService (Story 2.5已创建)
3. Message模型已支持image类型
4. 图片文件上传和存储

**Flutter (部分实现):**
1. Message模型添加isImage和imageUrl方法
2. ConversationService.sendImageMessage()方法

### 待完成部分 ⏳ (需要图片库)

**Flutter Libraries:**
```yaml
# pubspec.yaml (需要添加)
dependencies:
  image_picker: ^1.0.4        # 选择图片
  cached_network_image: ^3.3.0 # 缓存网络图片
  photo_view: ^0.14.0         # 图片查看器
  image: ^4.1.3               # 图片处理/压缩
  permission_handler: ^11.0.0 # 权限管理
```

**需要实现的Widget:**
1. `ImagePickerButton` - 图片选择按钮（相册/拍照）
2. `ImageMessageBubble` - 图片消息气泡
3. `ImageFullScreenViewer` - 全屏图片查看器
4. `ImageCompressor` - 图片压缩工具

---

## Files Created/Modified

### Backend

1. **backend/app/routers/conversation.py** (Updated +99 lines)
   - Import file_storage service (已在Story 2.5导入)
   - POST /conversations/{id}/messages/image endpoint
   - 图片文件上传处理
   - 创建image类型消息
   - AI生成文本回复（MVP简化）

2. **backend/app/services/file_storage.py** (Already exists from Story 2.5)
   - save_image_file()方法已实现
   - 支持JPG/JPEG/PNG/GIF/WEBP
   - 5MB大小限制
   - UUID唯一文件名

### Frontend

1. **lib/features/conversation/models/message.dart** (Updated +6 lines)
   - 添加isImage getter方法
   - 添加imageUrl getter方法

2. **lib/features/conversation/services/conversation_service.dart** (Updated +74 lines)
   - 添加sendImageMessage()方法
   - 使用MultipartRequest上传
   - 错误处理（401, 404, 413, 500）

---

## API Endpoints

### POST /api/v1/conversations/{conversation_id}/messages/image

**Authentication:** Required (JWT Bearer token)

**Request (multipart/form-data):**
```
Content-Type: multipart/form-data

image_file: (binary image file, JPG/PNG/GIF/WEBP)
```

**Success Response (200 OK):**
```json
{
  "user_message": {
    "id": 15,
    "conversation_id": 1,
    "sender_type": "user",
    "message_type": "image",
    "content": "[图片]",
    "voice_url": "/uploads/images/1_f9a3c7e2-b8d1-4a5e-8c2f-6d9e1b3a5c7f.jpg",
    "voice_duration": null,
    "emotion": null,
    "timestamp": "2026-01-13T15:00:00Z",
    "status": "sent"
  },
  "idol_reply": {
    "id": 16,
    "conversation_id": 1,
    "sender_type": "idol",
    "message_type": "text",
    "content": "哇~看起来是张不错的照片呢！谢谢分享~",
    "voice_url": null,
    "voice_duration": null,
    "emotion": "friendly",
    "timestamp": "2026-01-13T15:00:02Z",
    "status": "delivered"
  }
}
```

**Error Responses:**
- `400 Bad Request`: 不支持的图片格式
- `401 Unauthorized`: 未登录
- `404 Not Found`: 对话不存在
- `413 Payload Too Large`: 图片超过5MB
- `500 Internal Server Error`: 文件保存失败

---

## Technical Decisions

### 1. MVP简化：AI通用回复（不做图像识别）
**Decision:** 用户发送图片，AI回复通用文本（不识别图片内容）
**Rationale:**
- 图像识别（Vision API）需要额外服务和成本
  - GPT-4 Vision: ~$0.01/image
  - Claude 3 Vision: ~$0.015/image
  - Google Cloud Vision API
- MVP阶段不是核心功能
- 可以显示图片发送成功，偶像知道收到图片

**MVP流程:**
```
用户 → 发送图片 → 保存文件 → 创建image消息
     → AI收到提示"用户发送了一张图片"
     → AI生成通用文本回复（如"看起来是张不错的照片呢~"）
```

**Future完整版:**
```
用户 → 发送图片 → Vision API识别内容
     → AI分析图片内容（人物/场景/物品/文字）
     → AI生成针对性回复（如"你的猫咪好可爱！"）
     → 可选：根据图片情绪调整回复语气
```

### 2. 复用voice_url字段存储图片URL（MVP）
**Decision:** 图片URL存储在voice_url字段，不新增image_url字段
**Rationale:**
- MVP简化数据库结构
- voice_url和image_url互斥（消息只能是一种类型）
- message_type字段已经区分类型
- 减少迁移复杂度

**Future:** 可重命名为media_url或添加专门的image_url字段

### 3. 文件大小限制5MB
**Decision:** 图片文件最大5MB
**Rationale:**
- 5MB适合高质量手机照片
- 防止存储爆炸
- 前端可压缩后再上传

**压缩策略（Future）:**
```dart
// 上传前压缩
final compressedImage = await FlutterImageCompress.compressWithFile(
  imagePath,
  minWidth: 1920,
  minHeight: 1080,
  quality: 85, // 0-100
);
```

### 4. 支持的图片格式
**Decision:** 支持JPG, PNG, GIF, WEBP
**Rationale:**
- JPG/PNG: 最常见的手机照片格式
- GIF: 支持动图（聊天常用）
- WEBP: 现代压缩格式，更小的文件体积

**不支持:**
- BMP: 文件过大
- TIFF: 专业格式，手机不常用
- SVG: 矢量图，聊天场景少

### 5. 本地存储（不用云存储）
**Decision:** 存储到服务器uploads/images/目录
**Rationale:**
- 与Story 2.5语音消息保持一致
- MVP简化开发
- 后续可迁移到云存储（OSS/S3）

**Future Cloud Storage:**
- CDN加速图片加载
- 自动生成缩略图
- 图片处理（裁剪/水印）

---

## Flutter Implementation Guide (待实现)

### 安装依赖

```yaml
# pubspec.yaml
dependencies:
  image_picker: ^1.0.4        # 选择图片
  cached_network_image: ^3.3.0 # 网络图片缓存
  photo_view: ^0.14.0         # 全屏查看
  image: ^4.1.3               # 图片压缩
  permission_handler: ^11.0.0 # 权限
```

### ImagePickerButton示例

```dart
// lib/features/conversation/widgets/image_picker_button.dart

class ImagePickerButton extends StatelessWidget {
  final Function(String imagePath) onImageSelected;

  const ImagePickerButton({required this.onImageSelected});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(Icons.image),
      onPressed: () => _showImageSourceDialog(context),
    );
  }

  Future<void> _showImageSourceDialog(BuildContext context) async {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.photo_library),
              title: Text('从相册选择'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
            ListTile(
              leading: Icon(Icons.camera_alt),
              title: Text('拍照'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();

    // Request permission
    if (source == ImageSource.camera) {
      if (!await Permission.camera.request().isGranted) {
        return;
      }
    } else {
      if (!await Permission.photos.request().isGranted) {
        return;
      }
    }

    // Pick image
    final XFile? image = await picker.pickImage(
      source: source,
      maxWidth: 1920,
      maxHeight: 1080,
      imageQuality: 85, // 压缩质量
    );

    if (image != null) {
      onImageSelected(image.path);
    }
  }
}
```

### ImageMessageBubble示例

```dart
// lib/features/conversation/widgets/image_message_bubble.dart

class ImageMessageBubble extends StatelessWidget {
  final Message message;

  const ImageMessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => _showFullScreen(context),
      child: Container(
        constraints: BoxConstraints(
          maxWidth: 250,
          maxHeight: 350,
        ),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: Colors.grey.shade200,
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: CachedNetworkImage(
            imageUrl: message.imageUrl!,
            placeholder: (context, url) => Center(
              child: CircularProgressIndicator(),
            ),
            errorWidget: (context, url, error) => Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error, color: Colors.red),
                  Text('图片加载失败'),
                ],
              ),
            ),
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }

  void _showFullScreen(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ImageFullScreenViewer(
          imageUrl: message.imageUrl!,
        ),
      ),
    );
  }
}
```

### ImageFullScreenViewer示例

```dart
// lib/features/conversation/widgets/image_fullscreen_viewer.dart

class ImageFullScreenViewer extends StatelessWidget {
  final String imageUrl;

  const ImageFullScreenViewer({required this.imageUrl});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: PhotoView(
        imageProvider: CachedNetworkImageProvider(imageUrl),
        minScale: PhotoViewComputedScale.contained,
        maxScale: PhotoViewComputedScale.covered * 2,
        backgroundDecoration: BoxDecoration(color: Colors.black),
        loadingBuilder: (context, event) => Center(
          child: CircularProgressIndicator(
            value: event == null
                ? 0
                : event.cumulativeBytesLoaded / event.expectedTotalBytes!,
          ),
        ),
      ),
    );
  }
}
```

### 使用示例

```dart
// 在聊天界面

// 发送图片
ImagePickerButton(
  onImageSelected: (imagePath) async {
    try {
      final result = await conversationService.sendImageMessage(
        conversationId: conversationId,
        imagePath: imagePath,
      );

      // 添加消息到UI
      setState(() {
        messages.add(result['user_message']);
        messages.add(result['idol_reply']);
      });
    } catch (e) {
      // 显示错误
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('发送失败: $e')),
      );
    }
  },
)

// 显示图片消息
if (message.isImage) {
  ImageMessageBubble(message: message)
} else if (message.isText) {
  TextMessageBubble(message: message)
}
```

---

## Limitations & Future Work

### Current Limitations (MVP):

1. **无图像识别（Vision API）:** AI无法理解图片内容
2. **无自动压缩:** 依赖image_picker的压缩参数
3. **无缩略图:** 所有图片加载原图
4. **本地存储:** 无CDN，大流量时慢
5. **Flutter端未实现:** 选择器和显示UI待开发
6. **无多图发送:** 只能一次发一张
7. **无图片编辑:** 不能裁剪/滤镜/涂鸦

### Future Enhancements (Post-MVP):

1. **图像识别（Vision AI）:**
   - 集成GPT-4 Vision或Claude 3
   - 识别图片中的人物、场景、物品、文字
   - AI基于内容生成个性化回复
   - 情感分析（图片情绪）

2. **自动缩略图生成:**
   - 服务器端生成多种尺寸
   - 列表显示缩略图（快速加载）
   - 点击加载原图

3. **云存储 + CDN:**
   - 阿里云OSS或AWS S3
   - CDN加速全球访问
   - 自动清理过期图片

4. **高级图片处理:**
   - 智能裁剪
   - 滤镜和美颜
   - 涂鸦和文字标注
   - 压缩算法优化

5. **多图发送:**
   - 一次选择多张图片
   - 九宫格显示
   - 批量上传

6. **图片搜索:**
   - 按日期搜索图片
   - 按内容搜索（需Vision AI）
   - 生成相册

---

## Performance Considerations

1. **图片加载优化:**
   - 使用cached_network_image缓存
   - 列表显示缩略图
   - 懒加载（滚动时才加载）

2. **上传优化:**
   - 前端压缩后上传
   - 显示上传进度
   - 断点续传（Future）

3. **存储优化:**
   - 定期清理过期图片
   - 压缩存储（WEBP格式）
   - CDN分发

---

## Related Stories

- **Depends on:**
  - Story 2.5: 文件存储服务（FileStorageService）
  - Story 2.1: 基础对话API

- **Enables:**
  - Epic 4: 记忆系统（图片作为记忆触发）
  - Epic 5: 偶像生活（分享日常图片）
  - Future: 图片情感分析

---

## Acceptance Criteria Status

| AC | Status | Notes |
|----|--------|-------|
| AC1: 图片消息发送API | ✅ Done | POST /messages/image端点完成 |
| AC2: Message模型图片支持 | ✅ Done | isImage和imageUrl方法已添加 |
| AC3: 图片上传Service方法 | ✅ Done | sendImageMessage()完成 |
| AC4: 图片选择器集成 | ⏳ MVP Pending | 需添加image_picker库并实现UI |
| AC5: 图片消息显示Widget | ⏳ MVP Pending | 需添加cached_network_image并实现UI |

---

**Story 2.6 Complete (Backend)!** ✅

后端图片消息基础架构已完成，包括API端点和文件存储。Flutter端选择器和显示组件需要集成图片库（image_picker + cached_network_image）并实现UI。

**MVP现状:**
- ✅ 后端完整实现（API、文件存储）
- ✅ Flutter数据模型和Service方法
- ⏳ Flutter UI组件待实现（需图片库）

**下一步:**
1. 添加Flutter图片依赖（image_picker, cached_network_image, photo_view）
2. 实现ImagePickerButton组件
3. 实现ImageMessageBubble组件
4. 实现ImageFullScreenViewer组件
5. 集成相册/相机权限请求
6. 测试图片选择和上传流程

**Next Stories:**
- Story 2.7: Emoji库和快速发送
- Story 2.8: 对话历史和空闲状态管理
- Story 2.9: 错误处理和重试机制
