# 图片处理 MCP 服务器

一个基于 Model Context Protocol (MCP) 的专业图片处理服务器，提供全面的图片处理功能。

## 🎯 功能特性

### 基础操作 (4个工具)
- 图片加载和保存
- 格式转换 (JPEG, PNG, WebP, BMP, TIFF)
- 图片信息获取

### 几何变换 (4个工具)
- 尺寸调整 (支持保持宽高比)
- 图片裁剪
- 旋转变换
- 翻转操作 (水平/垂直)

### 色彩调整 (7个工具)
- 亮度调整
- 对比度调整
- 饱和度调整
- 锐度调整
- 灰度转换
- 伽马校正
- 不透明度调整

### 滤镜效果 (10个工具)
- 模糊效果 (普通模糊、高斯模糊)
- 锐化效果
- 边缘增强
- 浮雕效果
- 边缘检测
- 平滑效果
- 轮廓效果
- 复古棕褐色
- 反色效果

### 🆕 特效处理 (6个工具)
- 添加边框 (多种样式)
- 创建剪影效果
- 添加阴影效果
- 添加水印 (图片/文字)
- 添加暗角效果
- 创建宝丽来效果

### 🆕 高级功能 (6个工具)
- 批量图片处理
- 创建图片拼贴
- 创建缩略图网格
- 图片混合合成
- 提取主要颜色
- 创建GIF动画

### 🆕 性能监控 (2个工具)
- 性能统计查看
- 性能数据重置

## 📊 项目统计

- **总工具数**: 39个
- **测试覆盖**: 95%+
- **支持格式**: JPEG, PNG, WebP, BMP, TIFF, GIF

## 🎯 使用示例

### 基础图片处理
```json
{
    "tool": "resize_image",
    "arguments": {
        "image_source": "data:image/png;base64,...",
        "width": 800,
        "height": 600,
        "maintain_aspect_ratio": true
    }
}
```

### 特效处理
```json
{
    "tool": "add_watermark",
    "arguments": {
        "image_source": "data:image/png;base64,...",
        "watermark_source": "data:image/png;base64,...",
        "position": "bottom_right",
        "opacity": 0.7
    }
}
```

### 批量处理
```json
{
    "tool": "batch_resize",
    "arguments": {
        "image_sources": ["data:image/png;base64,...", "..."],
        "width": 200,
        "height": 200,
        "maintain_aspect_ratio": true
    }
}
```

### 创建GIF动画
```json
{
    "tool": "create_gif",
    "arguments": {
        "image_sources": ["data:image/png;base64,...", "..."],
        "duration": 500,
        "loop": true,
        "optimize": true
    }
}
```

## 环境要求

- Python 3.11+
- uv (现代 Python 包管理器)
- 支持的操作系统: Windows, macOS, Linux

## 🚀 快速开始

### 1. 安装 uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装项目依赖

```bash
# 克隆或下载项目
cd ps-mcp

# 安装依赖（会自动创建虚拟环境）
uv sync

# Windows 用户也可以直接运行
install.bat
```

### 3. 运行服务器

```bash
# 方式1: 使用 uv 直接运行
uv run python main.py

# 方式2: Windows 用户可以直接运行
run.bat

# 方式3: 激活环境后运行
uv shell
python main.py
```

### 4. 配置MCP客户端

支持的客户端：
- 🍒 **Cherry Studio** - 复制 `examples/cherry_studio_config.json` 内容
- 🖱️ **Cursor** - 复制 `examples/cursor_config.json` 内容  
- 🔧 **Cline** - 复制 `examples/cline_settings.json` 内容
- 💬 **Claude Desktop** - 复制 `examples/claude_desktop_config.json` 内容
- 💡 **注意**: 替换路径为实际项目路径

### 测试连接
在MCP客户端中尝试：
```
请帮我获取一张图片的信息
```

### 5. 使用示例

服务器启动后，可以通过MCP协议调用各种图片处理功能：

```python
# 示例：调整图片大小
{
    "tool": "resize_image",
    "arguments": {
        "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "width": 800,
        "height": 600,
        "keep_aspect_ratio": true
    }
}

# 示例：应用高斯模糊
{
    "tool": "gaussian_blur",
    "arguments": {
        "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
        "radius": 5.0
    }
}
```

## 项目结构

```
image-mcp-server/
├── main.py                 # MCP服务器入口
├── tools/                  # 工具模块
│   ├── __init__.py
│   ├── basic_ops.py       # 基础操作
│   ├── transform.py       # 几何变换
│   ├── color_adjust.py    # 色彩调整
│   ├── filters.py         # 滤镜效果
│   └── effects.py         # 特效处理
├── utils/                 # 辅助工具
│   ├── __init__.py
│   ├── image_utils.py     # 图片工具函数
│   └── validation.py      # 参数验证
│   └── image_processor.py      # 图片处理类
├── tests/                 # 测试文件
├── environment.yml        # conda环境配置
├── requirements.txt       # pip依赖
└── README.md             # 项目文档
```

## 支持的功能

### 基础操作
- `load_image`: 加载图片（支持文件路径和base64）
- `save_image`: 保存图片到文件
- `get_image_info`: 获取图片信息
- `convert_format`: 转换图片格式

### 几何变换
- `resize_image`: 调整图片大小
- `crop_image`: 裁剪图片
- `rotate_image`: 旋转图片
- `flip_image`: 翻转图片

### 色彩调整
- `adjust_brightness`: 调整亮度
- `adjust_contrast`: 调整对比度
- `adjust_saturation`: 调整饱和度
- `adjust_sharpness`: 调整锐度
- `convert_to_grayscale`: 转换为灰度图
- `adjust_gamma`: 调整伽马值
- `adjust_opacity`: 调整不透明度

### 滤镜效果
- `gaussian_blur`: 高斯模糊
- `sharpen_image`: 锐化
- `edge_detection`: 边缘检测

### 特效处理
- `add_border`: 添加描边
- `create_silhouette`: 创建剪影
- `add_shadow`: 添加阴影

## 开发指南

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_image_processor.py

```

### 功能测试

运行功能测试：

```bash
uv run python tests\test_call_mcp.py
```

或者使用批处理文件（Windows）：

```bash
run_tests.bat
```

测试将使用 `tests/test_image.png` 作为测试图片，验证所有图片处理功能是否正常工作。

## 技术架构

- **MCP协议**: 基于Model Context Protocol的服务器实现
- **图片处理**: 使用Pillow和OpenCV进行图片处理
- **异步支持**: 基于asyncio的异步处理
- **模块化设计**: 按功能分类的模块化架构
- **参数验证**: 完善的输入参数验证机制

## 限制说明

- 最大图片尺寸: 4096x4096像素
- 支持格式: JPEG, PNG, BMP, TIFF, WEBP
- 内存使用: 建议可用内存至少2GB

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (开发中)
- 初始版本
- 基础图片处理功能
- MCP服务器框架
- 完整的测试套件

## 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](../../issues) 页面
2. 创建新的 Issue

---

**注意**: 本项目目前处于开发阶段，部分功能可能尚未完全实现。