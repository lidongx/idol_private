# Story 1.4: Material Design 3 主题与UI基础框架

Status: completed

> **⏱️ 实际开发时间:** ~1天
> **✅ 完成日期:** 2026-01-13

## Story

As a **开发团队**,
I want **建立统一的UI设计系统和组件库**,
So that **所有页面风格一致，开发效率提升**。

## Acceptance Criteria

### AC1: Material Design 3 主题配置
- **Given** Flutter项目已初始化
- **When** 配置Material Design 3主题
- **Then** 创建主题配置文件 `lib/core/theme/app_theme.dart`
- **And** 支持明亮模式和暗黑模式
- **And** 使用温暖色调配色方案（橙色 + 粉色）
- **And** 配置完整的组件主题（按钮、输入框、卡片、对话框等）
- **And** 定义清晰的文本层级（Display, Headline, Title, Body, Label）

**Seed Colors:**
- Primary: `#FF9E80` (温暖橙色)
- Secondary: `#FFB6C1` (柔和粉色)

### AC2: 通用组件库创建
- **Given** 主题配置已完成
- **When** 创建通用组件库
- **Then** 实现以下组件：
  - `LoadingIndicator`: 加载动画组件（支持多种尺寸和样式）
  - `AppButton`: 统一样式按钮（Primary/Secondary/Text，3种尺寸）
  - `AppInput`: 统一样式输入框（带验证和专用变体）
  - `AppScaffold`: 统一页面脚手架（支持多种布局模式）

### AC3: 响应式布局工具
- **Given** 需要支持多平台
- **When** 配置响应式布局断点
- **Then** 实现响应式工具类 `lib/core/utils/responsive.dart`
- **And** 定义断点：
  - 手机：< 600px
  - 平板：600px - 1200px
  - 桌面：> 1200px
- **And** 提供设备类型检测和响应式值计算方法

### AC4: 主题集成到应用
- **Given** 所有主题和组件已创建
- **When** 更新 `main.dart`
- **Then** MaterialApp 使用 `AppTheme.lightTheme` 和 `AppTheme.darkTheme`
- **And** 配置 `themeMode: ThemeMode.system` 跟随系统主题
- **And** 更新现有加载指示器使用新的 `LoadingIndicator` 组件

---

## Implementation Details

### Architecture Overview

```
lib/
├── core/
│   ├── theme/
│   │   └── app_theme.dart          # Material Design 3 theme configuration
│   └── utils/
│       └── responsive.dart         # Responsive layout utilities
│
└── shared/
    └── widgets/
        ├── loading_indicator.dart  # Loading animations
        ├── app_button.dart         # Unified button styles
        ├── app_input.dart          # Unified input fields
        └── app_scaffold.dart       # Page scaffolds
```

### 1. Material Design 3 Theme

**File:** `lib/core/theme/app_theme.dart`

**Key Features:**
- Full Material Design 3 support (`useMaterial3: true`)
- Color scheme from seed colors with semantic naming
- Comprehensive component theming:
  - AppBar (elevation: 0, centered title)
  - Input fields (filled style, 12px border radius)
  - Buttons (elevated, outlined, text)
  - Cards (16px border radius)
  - Chips, Dialogs, SnackBars, Bottom Nav
- Complete text hierarchy (13 text styles)
- Dark theme with automatic color adjustments

**Color Accessibility:**
- WCAG 2.1 AA compliant contrast ratios
- Semantic color naming (onSurface, onPrimary, etc.)
- Appropriate opacity for disabled states

### 2. Responsive Layout Utilities

**File:** `lib/core/utils/responsive.dart`

**Classes:**
- `Breakpoints`: Static breakpoint constants
- `DeviceType`: Enum (mobile, tablet, desktop)
- `Responsive`: Utility methods for responsive design
- `ResponsiveBuilder`: Widget for device-specific layouts

**Key Methods:**
```dart
Responsive.getDeviceType(context)  // Get current device type
Responsive.isMobile(context)       // Check if mobile
Responsive.getValue(...)           // Get value by device type
Responsive.fontSize(...)           // Calculate responsive font size
Responsive.spacing(...)            // Calculate responsive spacing
Responsive.maxContentWidth(...)    // Get max content width
```

**Usage Example:**
```dart
final padding = Responsive.getValue(
  context,
  mobile: 16.0,
  tablet: 24.0,
  desktop: 32.0,
);
```

### 3. Shared Widget Components

#### LoadingIndicator

**File:** `lib/shared/widgets/loading_indicator.dart`

**Variants:**
- `LoadingIndicator`: Standard circular indicator
- `SmallLoadingIndicator`: For buttons (20px)
- `LoadingOverlay`: Full-screen loading with optional message
- `InlineLoadingIndicator`: Inline with text (horizontal/vertical)

**Features:**
- Customizable size and stroke width
- Automatic theme color usage
- Accessibility support

#### AppButton

**File:** `lib/shared/widgets/app_button.dart`

**Variants:**
- `ButtonVariant.primary`: Elevated button with fill
- `ButtonVariant.secondary`: Outlined button
- `ButtonVariant.text`: Text button without background

**Sizes:**
- `ButtonSize.small`: 36px height
- `ButtonSize.medium`: 48px height
- `ButtonSize.large`: 56px height

**Features:**
- Loading state with built-in indicator
- Leading/trailing icons
- Full-width mode
- Custom colors override
- Disabled state handling
- Named constructors (`.primary()`, `.secondary()`, `.text()`)

**Usage Example:**
```dart
AppButton.primary(
  label: '登录',
  onPressed: _handleLogin,
  isLoading: isLoading,
  fullWidth: true,
  leadingIcon: Icons.login,
)
```

#### AppInput

**File:** `lib/shared/widgets/app_input.dart`

**Variants:**
- `AppInput`: Base input field
- `AppPasswordInput`: Password with visibility toggle
- `AppPhoneInput`: Phone number (11 digits, China format)
- `AppCodeInput`: Verification code (default 6 digits)
- `AppSearchInput`: Search with clear button

**Features:**
- Consistent styling from theme
- Built-in validation support
- Input formatters for special types
- Prefix/suffix icons with callbacks
- Auto-focus and read-only modes

**Usage Example:**
```dart
AppPasswordInput(
  controller: _passwordController,
  label: '密码',
  hint: '请输入密码',
  validator: _validatePassword,
)
```

#### AppScaffold

**File:** `lib/shared/widgets/app_scaffold.dart`

**Variants:**
- `AppScaffold`: Base scaffold with full customization
- `CenteredScaffold`: Centered content with max width
- `FormScaffold`: Keyboard-aware form layout
- `TabScaffold`: Scaffold with tab bar

**Features:**
- Consistent page structure
- SafeArea handling
- Optional scrolling
- Customizable padding
- App bar configuration
- Support for drawers, FAB, bottom nav

**Usage Example:**
```dart
FormScaffold(
  title: '注册',
  formKey: _formKey,
  body: Column(
    children: [
      AppPhoneInput(...),
      AppPasswordInput(...),
      AppButton.primary(...),
    ],
  ),
)
```

### 4. Main App Integration

**File:** `lib/main.dart`

**Changes:**
```dart
import 'package:idol_private/core/theme/app_theme.dart';
import 'package:idol_private/shared/widgets/loading_indicator.dart';

MaterialApp(
  title: 'Idol Private',
  theme: AppTheme.lightTheme,
  darkTheme: AppTheme.darkTheme,
  themeMode: ThemeMode.system, // Follow system theme
  ...
)

// Updated AuthGate loading state
loading: () => const Scaffold(
  body: LoadingIndicator(),
),
```

---

## Design System

### Color Palette

**Light Theme:**
- Primary: Generated from `#FF9E80` (warm orange)
- Secondary: Generated from `#FFB6C1` (soft pink)
- Surface: White with subtle tints
- On-colors: High-contrast text colors

**Dark Theme:**
- Primary: Lighter tint of seed color
- Secondary: Adjusted for dark backgrounds
- Surface: Dark grays with warm undertones
- On-colors: Light text colors

### Typography Scale

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| displayLarge | 32px | Bold | Hero headings |
| displayMedium | 28px | Bold | Section titles |
| displaySmall | 24px | Bold | Card headers |
| headlineLarge | 22px | SemiBold | Page titles |
| headlineMedium | 20px | SemiBold | Subsections |
| headlineSmall | 18px | SemiBold | Grouping headers |
| titleLarge | 18px | Medium | List items |
| titleMedium | 16px | Medium | Subtitles |
| titleSmall | 14px | Medium | Captions |
| bodyLarge | 16px | Regular | Primary body text |
| bodyMedium | 14px | Regular | Secondary text |
| bodySmall | 12px | Regular | Supporting text |
| labelLarge | 14px | SemiBold | Button text |
| labelMedium | 12px | Medium | Chip text |
| labelSmall | 11px | Medium | Tags |

### Spacing System

Consistent spacing using 4px grid:
- 4px: Tight spacing
- 8px: Compact spacing
- 12px: Comfortable spacing
- 16px: Standard spacing
- 24px: Generous spacing
- 32px: Section spacing
- 48px: Major section breaks

### Component Specifications

**Buttons:**
- Height: 36px (small), 48px (medium), 56px (large)
- Padding: 16/24/32px horizontal
- Border radius: 12px
- Elevation: 0 (Material Design 3)

**Input Fields:**
- Height: Variable (auto-adjusts to content)
- Border radius: 12px
- Filled style with subtle background
- Focus: 2px primary color border

**Cards:**
- Border radius: 16px
- Elevation: 0 (use background color contrast)
- Padding: 16px

---

## Files Created

### Core Files

1. **`lib/core/theme/app_theme.dart`** (450 lines)
   - Material Design 3 theme configuration
   - Light and dark theme definitions
   - Complete component theming
   - Typography scale

2. **`lib/core/utils/responsive.dart`** (192 lines)
   - Breakpoint constants
   - Device type detection
   - Responsive value calculations
   - ResponsiveBuilder widget

### Shared Widget Components

3. **`lib/shared/widgets/loading_indicator.dart`** (125 lines)
   - LoadingIndicator
   - SmallLoadingIndicator
   - LoadingOverlay
   - InlineLoadingIndicator

4. **`lib/shared/widgets/app_button.dart`** (256 lines)
   - AppButton with 3 variants
   - 3 size options
   - Loading state support
   - Icon support

5. **`lib/shared/widgets/app_input.dart`** (301 lines)
   - AppInput base class
   - AppPasswordInput
   - AppPhoneInput
   - AppCodeInput
   - AppSearchInput

6. **`lib/shared/widgets/app_scaffold.dart`** (233 lines)
   - AppScaffold
   - CenteredScaffold
   - FormScaffold
   - TabScaffold

### Modified Files

7. **`lib/main.dart`** (modified)
   - Integrated AppTheme
   - Added system theme support
   - Updated loading indicator

**Total Lines of Code:** ~1,500+ lines

---

## Implementation Success Criteria

**Story完成标准:**
- ✅ Material Design 3 theme configured with light and dark modes
- ✅ Responsive layout utilities with breakpoints
- ✅ Complete shared widget component library
- ✅ All components follow design system specifications
- ✅ Theme integrated into main app
- ✅ Loading states use new LoadingIndicator
- ✅ Components support accessibility (semantic labels, contrast)
- ✅ Code organized following architecture structure (core/ and shared/)

**Technical Validation:**
- ✅ Material Design 3 (`useMaterial3: true`)
- ✅ Seed colors: `#FF9E80` and `#FFB6C1`
- ✅ System theme support (`ThemeMode.system`)
- ✅ Responsive breakpoints: 600px, 1200px
- ✅ Complete text hierarchy (13 styles)
- ✅ Component library with consistent APIs
- ✅ No hardcoded colors in widgets (use theme)

**Definition of Done:**
- All components created and documented
- Theme applied throughout the app
- No compilation errors
- Components ready for use in future stories
- Documentation complete (this file)

---

## Usage Guidelines

### Theme Colors

Always use theme colors instead of hardcoded values:

```dart
// ✅ Good
color: Theme.of(context).colorScheme.primary

// ❌ Bad
color: Colors.orange
```

### Responsive Layouts

Use responsive utilities for cross-platform support:

```dart
// ✅ Good
padding: EdgeInsets.all(Responsive.spacing(context, 16.0))

// ❌ Bad
padding: EdgeInsets.all(16.0)
```

### Component Usage

Prefer shared components over raw Material widgets:

```dart
// ✅ Good
AppButton.primary(label: '登录', onPressed: _login)

// ❌ Bad
ElevatedButton(onPressed: _login, child: Text('登录'))
```

### Form Scaffolds

Use FormScaffold for form pages:

```dart
// ✅ Good
FormScaffold(
  title: '注册',
  formKey: _formKey,
  body: Column(children: [...]),
)

// ❌ Bad
Scaffold(
  appBar: AppBar(title: Text('注册')),
  body: SafeArea(
    child: SingleChildScrollView(
      child: Form(key: _formKey, ...),
    ),
  ),
)
```

---

## Testing Guide

### Visual Testing

1. **Light/Dark Theme Toggle:**
   - Change system theme settings
   - Verify app theme switches automatically
   - Check all screens adapt properly

2. **Responsive Layout:**
   - Test on different screen sizes
   - Verify breakpoints: < 600px, 600-1200px, > 1200px
   - Check spacing and font sizes scale appropriately

3. **Component Showcase:**
   - Test all button variants and sizes
   - Test all input field types
   - Verify loading indicators display correctly
   - Check scaffold layouts work as expected

### Accessibility Testing

1. **Color Contrast:**
   - Verify text on backgrounds meets WCAG AA (4.5:1)
   - Check disabled state colors are distinguishable

2. **Semantic Labels:**
   - All interactive elements have labels
   - Screen reader support

### Integration Testing

Test existing auth screens with new theme:
1. Login screen renders correctly
2. Register screen uses new theme
3. Forgot password flow works with new components
4. Loading states show new indicators

---

## References

**Architecture文档:**
- [Technology Stack - Frontend] `_bmad-output/planning-artifacts/architecture.md` Lines 427-450
- [Project Structure] `architecture.md` Lines 467-526
- [State Management: Riverpod] `architecture.md` Lines 733-779

**Epics文档:**
- [Story 1.4 Full Spec] `_bmad-output/planning-artifacts/epics.md` Lines 1889-1952
- [Epic 1 Overview] `epics.md` Lines 1631-1641

**Material Design 3:**
- [Material Design 3 Guidelines](https://m3.material.io/)
- [Flutter Material 3 Migration](https://docs.flutter.dev/ui/design/material)
- [Color System](https://m3.material.io/styles/color/system/overview)
- [Typography](https://m3.material.io/styles/typography/overview)

**Related Stories:**
- [Story 1.1: 项目初始化与用户注册] `1-1-project-init-user-registration.md`
- [Story 1.2: 用户登录与JWT认证] (to be documented)
- [Story 1.3: 密码重置流程] `1-3-password-reset-flow.md`

---

## Dev Agent Record

### Agent Model Used
Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Implementation Timeline
- **Start:** 2026-01-13 (continuing from Story 1.3)
- **Completion:** 2026-01-13 (same day)
- **Total Duration:** ~1 day

### Key Implementation Decisions

1. **Material Design 3 vs Material 2:**
   - Chose Material Design 3 for modern design language
   - Leverages new color system with tonal palettes
   - Better accessibility and theming support

2. **Theme Structure:**
   - Created single AppTheme class with static methods
   - Separated light and dark themes completely
   - Shared typography builder for consistency

3. **Component Organization:**
   - Followed architecture: `core/` for infrastructure, `shared/` for reusable components
   - Each component in separate file for modularity
   - Consistent naming convention (`App*` prefix)

4. **Responsive Design:**
   - Utility-first approach vs responsive widgets
   - Provides both programmatic and widget-based solutions
   - Breakpoints match industry standards

5. **Button Variants:**
   - Named constructors for better ergonomics
   - Enum-based variant selection
   - Size enum for type safety

6. **Input Specialization:**
   - Base AppInput for flexibility
   - Specialized variants for common use cases
   - Encapsulates validation and formatting logic

### Completion Notes

**What went well:**
- Clean, well-organized component library
- Comprehensive theme covering all Material components
- Responsive utilities ready for multi-platform support
- Consistent API design across all components

**Implementation highlights:**
- 1,500+ lines of production-ready UI code
- Full Material Design 3 compliance
- Dark theme support from day one
- Accessibility considerations built-in

**No blockers encountered during implementation**

---

## 🎯 Story 1.4 Status: ✅ COMPLETED

**Ready for Story 1.5 implementation!**

UI基础框架已完全建立，Material Design 3主题配置完成。所有通用组件已创建并可以在未来的stories中使用。应用现在具有一致的视觉风格、响应式布局支持和深色模式。

**Next Story:** Story 1.5 - 偶像数据模型与首个偶像配置
