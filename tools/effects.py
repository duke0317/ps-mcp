"""
特效处理模块

提供高级图片特效处理功能，包括描边、阴影、剪影等特殊效果。
"""

from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
from mcp.types import Tool, TextContent
import json
import asyncio

from utils.image_processor import ImageProcessor
from utils.validation import (
    validate_image_source, validate_numeric_range, validate_color_hex,
    ensure_valid_image_source, ValidationError
)
from config import (
    MAX_IMAGE_SIZE, MIN_DIMENSION, MAX_BLUR_RADIUS,
    DEFAULT_FORMAT, DEFAULT_QUALITY, DEFAULT_IMAGE_FORMAT
)

def get_effect_tools() -> List[Tool]:
    """
    返回特效处理工具列表
    
    Returns:
        List[Tool]: 特效处理工具列表
    """
    return [
        Tool(
            name="add_border",
            description="为图片添加边框效果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "border_width": {
                        "type": "integer",
                        "description": "边框宽度（像素）",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10
                    },
                    "border_color": {
                        "type": "string",
                        "description": "边框颜色（十六进制格式，如#FF0000）",
                        "default": "#000000"
                    },
                    "border_style": {
                        "type": "string",
                        "description": "边框样式",
                        "enum": ["solid", "rounded", "shadow"],
                        "default": "solid"
                    },
                    "corner_radius": {
                        "type": "integer",
                        "description": "圆角半径（仅当border_style为rounded时有效）",
                        "minimum": 0,
                        "maximum": 50,
                        "default": 10
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="create_silhouette",
            description="创建图片的剪影效果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "silhouette_color": {
                        "type": "string",
                        "description": "剪影颜色（十六进制格式）",
                        "default": "#000000"
                    },
                    "background_color": {
                        "type": "string",
                        "description": "背景颜色（十六进制格式，transparent表示透明）",
                        "default": "transparent"
                    },
                    "threshold": {
                        "type": "integer",
                        "description": "透明度阈值（0-255）",
                        "minimum": 0,
                        "maximum": 255,
                        "default": 128
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="add_shadow",
            description="为图片添加阴影效果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "shadow_color": {
                        "type": "string",
                        "description": "阴影颜色（十六进制格式）",
                        "default": "#808080"
                    },
                    "shadow_offset_x": {
                        "type": "integer",
                        "description": "阴影X轴偏移（像素）",
                        "minimum": -50,
                        "maximum": 50,
                        "default": 5
                    },
                    "shadow_offset_y": {
                        "type": "integer",
                        "description": "阴影Y轴偏移（像素）",
                        "minimum": -50,
                        "maximum": 50,
                        "default": 5
                    },
                    "shadow_blur": {
                        "type": "integer",
                        "description": "阴影模糊半径",
                        "minimum": 0,
                        "maximum": 20,
                        "default": 5
                    },
                    "shadow_opacity": {
                        "type": "number",
                        "description": "阴影透明度（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="add_watermark",
            description="为图片添加水印",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "watermark_text": {
                        "type": "string",
                        "description": "水印文字（与watermark_image二选一）"
                    },
                    "watermark_image": {
                        "type": "string",
                        "description": "水印图片源（与watermark_text二选一）"
                    },
                    "position": {
                        "type": "string",
                        "description": "水印位置",
                        "enum": ["top-left", "top-right", "bottom-left", "bottom-right", "center"],
                        "default": "bottom-right"
                    },
                    "opacity": {
                        "type": "number",
                        "description": "水印透明度（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    },
                    "scale": {
                        "type": "number",
                        "description": "水印缩放比例",
                        "minimum": 0.1,
                        "maximum": 2.0,
                        "default": 0.2
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="apply_vignette",
            description="为图片添加暗角效果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "intensity": {
                        "type": "number",
                        "description": "暗角强度（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    },
                    "radius": {
                        "type": "number",
                        "description": "暗角半径（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7
                    },
                    "color": {
                        "type": "string",
                        "description": "暗角颜色（十六进制格式）",
                        "default": "#000000"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="create_polaroid",
            description="创建宝丽来照片效果",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "border_width": {
                        "type": "integer",
                        "description": "边框宽度（像素）",
                        "minimum": 10,
                        "maximum": 100,
                        "default": 40
                    },
                    "bottom_border": {
                        "type": "integer",
                        "description": "底部边框宽度（像素）",
                        "minimum": 20,
                        "maximum": 200,
                        "default": 80
                    },
                    "border_color": {
                        "type": "string",
                        "description": "边框颜色（十六进制格式）",
                        "default": "#FFFFFF"
                    },
                    "rotation": {
                        "type": "number",
                        "description": "旋转角度（度）",
                        "minimum": -15,
                        "maximum": 15,
                        "default": 0
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_source"]
            }
        )
    ]

# 特效处理函数实现

async def add_border(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    为图片添加边框效果
    
    Args:
        arguments: 包含图片源和边框参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        border_width = arguments.get("border_width", 10)
        border_color = arguments.get("border_color", "#000000")
        border_style = arguments.get("border_style", "solid")
        corner_radius = arguments.get("corner_radius", 10)
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(border_width, 1, 100, "border_width")
        validate_color_hex(border_color)
        validate_numeric_range(corner_radius, 0, 50, "corner_radius")
        
        # 加载图片
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 创建带边框的新图片
        new_width = image.width + 2 * border_width
        new_height = image.height + 2 * border_width
        
        if border_style == "rounded":
            # 圆角边框
            bordered_image = Image.new("RGBA", (new_width, new_height), border_color)
            
            # 创建圆角遮罩
            mask = Image.new("L", (new_width, new_height), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle(
                [0, 0, new_width, new_height],
                radius=corner_radius,
                fill=255
            )
            
            # 应用遮罩
            bordered_image.putalpha(mask)
            
            # 粘贴原图片
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            bordered_image.paste(image, (border_width, border_width), image)
            
        elif border_style == "shadow":
            # 阴影边框
            bordered_image = Image.new("RGBA", (new_width + 10, new_height + 10), (0, 0, 0, 0))
            
            # 创建阴影
            shadow = Image.new("RGBA", (new_width, new_height), border_color + "80")
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
            bordered_image.paste(shadow, (10, 10), shadow)
            
            # 粘贴原图片
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            bordered_image.paste(image, (border_width, border_width), image)
            
        else:
            # 实心边框
            bordered_image = Image.new("RGB", (new_width, new_height), border_color)
            bordered_image.paste(image, (border_width, border_width))
        
        # 转换为base64
        result_base64 = processor.image_to_base64(bordered_image, output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"成功添加{border_style}边框效果",
                "data": {
                    "image_data": result_base64,
                    "metadata": {
                        "original_size": f"{image.width}x{image.height}",
                        "new_size": f"{bordered_image.width}x{bordered_image.height}",
                        "border_width": border_width,
                        "border_color": border_color,
                        "border_style": border_style,
                        "format": output_format
                    }
                }
            }, ensure_ascii=False)
        )]
        
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"参数验证失败: {str(e)}"
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"添加边框失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def create_silhouette(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    创建图片的剪影效果
    
    Args:
        arguments: 包含图片源和剪影参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        silhouette_color = arguments.get("silhouette_color", "#000000")
        background_color = arguments.get("background_color", "transparent")
        threshold = arguments.get("threshold", 128)
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_color_hex(silhouette_color)
        if background_color != "transparent":
            validate_color_hex(background_color)
        validate_numeric_range(threshold, 0, 255, "threshold")
        
        # 加载图片
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 转换为RGBA模式
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # 创建剪影
        silhouette = Image.new("RGBA", image.size, (0, 0, 0, 0))
        
        # 获取像素数据
        pixels = image.load()
        silhouette_pixels = silhouette.load()
        
        # 解析剪影颜色
        silhouette_rgb = tuple(int(silhouette_color[i:i+2], 16) for i in (1, 3, 5))
        
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                
                # 如果像素不透明度大于阈值，则设为剪影颜色
                if a > threshold:
                    silhouette_pixels[x, y] = silhouette_rgb + (255,)
                else:
                    silhouette_pixels[x, y] = (0, 0, 0, 0)
        
        # 处理背景
        if background_color != "transparent":
            background_rgb = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5))
            final_image = Image.new("RGB", image.size, background_rgb)
            final_image.paste(silhouette, (0, 0), silhouette)
        else:
            final_image = silhouette
        
        # 转换为base64
        result_base64 = processor.image_to_base64(final_image, output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "成功创建剪影效果",
                "data": {
                    "image_data": result_base64,
                    "metadata": {
                        "size": f"{image.width}x{image.height}",
                        "silhouette_color": silhouette_color,
                        "background_color": background_color,
                        "threshold": threshold,
                        "format": output_format
                    }
                }
            }, ensure_ascii=False)
        )]
        
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"参数验证失败: {str(e)}"
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"创建剪影失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def add_shadow(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    为图片添加阴影效果
    
    Args:
        arguments: 包含图片源和阴影参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        shadow_color = arguments.get("shadow_color", "#808080")
        shadow_offset_x = arguments.get("shadow_offset_x", 5)
        shadow_offset_y = arguments.get("shadow_offset_y", 5)
        shadow_blur = arguments.get("shadow_blur", 5)
        shadow_opacity = arguments.get("shadow_opacity", 0.5)
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_color_hex(shadow_color)
        validate_numeric_range(shadow_offset_x, -50, 50, "shadow_offset_x")
        validate_numeric_range(shadow_offset_y, -50, 50, "shadow_offset_y")
        validate_numeric_range(shadow_blur, 0, 20, "shadow_blur")
        validate_numeric_range(shadow_opacity, 0.0, 1.0, "shadow_opacity")
        
        # 加载图片
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 转换为RGBA模式
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # 计算新图片尺寸（考虑阴影偏移和模糊）
        margin = shadow_blur + max(abs(shadow_offset_x), abs(shadow_offset_y))
        new_width = image.width + 2 * margin
        new_height = image.height + 2 * margin
        
        # 创建带阴影的新图片
        result_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
        
        # 创建阴影
        shadow_rgb = tuple(int(shadow_color[i:i+2], 16) for i in (1, 3, 5))
        shadow_alpha = int(255 * shadow_opacity)
        
        # 创建阴影图层
        shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        shadow_pixels = shadow_layer.load()
        image_pixels = image.load()
        
        # 根据原图的alpha通道创建阴影
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = image_pixels[x, y]
                if a > 0:
                    shadow_pixels[x, y] = shadow_rgb + (min(a, shadow_alpha),)
        
        # 应用模糊
        if shadow_blur > 0:
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
        
        # 计算阴影位置
        shadow_x = margin + shadow_offset_x
        shadow_y = margin + shadow_offset_y
        
        # 粘贴阴影
        result_image.paste(shadow_layer, (shadow_x, shadow_y), shadow_layer)
        
        # 粘贴原图片
        image_x = margin
        image_y = margin
        result_image.paste(image, (image_x, image_y), image)
        
        # 转换为base64
        result_base64 = processor.image_to_base64(result_image, output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "成功添加阴影效果",
                "data": {
                    "image_data": result_base64,
                    "metadata": {
                        "original_size": f"{image.width}x{image.height}",
                        "new_size": f"{result_image.width}x{result_image.height}",
                        "shadow_color": shadow_color,
                        "shadow_offset": f"({shadow_offset_x}, {shadow_offset_y})",
                        "shadow_blur": shadow_blur,
                        "shadow_opacity": shadow_opacity,
                        "format": output_format
                    }
                }
            }, ensure_ascii=False)
        )]
        
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"参数验证失败: {str(e)}"
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"添加阴影失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def add_watermark(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    为图片添加水印
    
    Args:
        arguments: 包含图片源和水印参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        watermark_text = arguments.get("watermark_text")
        watermark_image = arguments.get("watermark_image")
        position = arguments.get("position", "bottom-right")
        opacity = arguments.get("opacity", 0.5)
        scale = arguments.get("scale", 0.2)
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        if not watermark_text and not watermark_image:
            raise ValidationError("必须提供watermark_text或watermark_image之一")
        
        validate_numeric_range(opacity, 0.0, 1.0, "opacity")
        validate_numeric_range(scale, 0.1, 2.0, "scale")
        
        # 加载图片
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 转换为RGBA模式
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # 创建水印图层
        watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        
        if watermark_text:
            # 文字水印
            from PIL import ImageFont
            try:
                # 尝试使用系统字体
                font_size = int(min(image.width, image.height) * scale * 0.1)
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(watermark_layer)
            
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            if position == "top-left":
                x, y = 10, 10
            elif position == "top-right":
                x, y = image.width - text_width - 10, 10
            elif position == "bottom-left":
                x, y = 10, image.height - text_height - 10
            elif position == "bottom-right":
                x, y = image.width - text_width - 10, image.height - text_height - 10
            else:  # center
                x, y = (image.width - text_width) // 2, (image.height - text_height) // 2
            
            # 绘制文字
            alpha = int(255 * opacity)
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, alpha))
            
        else:
            # 图片水印
            watermark_img = processor.load_image(watermark_image)
            
            # 调整水印大小
            watermark_width = int(image.width * scale)
            watermark_height = int(watermark_img.height * watermark_width / watermark_img.width)
            watermark_img = watermark_img.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # 转换为RGBA
            if watermark_img.mode != "RGBA":
                watermark_img = watermark_img.convert("RGBA")
            
            # 调整透明度
            alpha_channel = watermark_img.split()[-1]
            alpha_channel = alpha_channel.point(lambda p: int(p * opacity))
            watermark_img.putalpha(alpha_channel)
            
            # 计算位置
            if position == "top-left":
                x, y = 10, 10
            elif position == "top-right":
                x, y = image.width - watermark_width - 10, 10
            elif position == "bottom-left":
                x, y = 10, image.height - watermark_height - 10
            elif position == "bottom-right":
                x, y = image.width - watermark_width - 10, image.height - watermark_height - 10
            else:  # center
                x, y = (image.width - watermark_width) // 2, (image.height - watermark_height) // 2
            
            # 粘贴水印
            watermark_layer.paste(watermark_img, (x, y), watermark_img)
        
        # 合成最终图片
        result_image = Image.alpha_composite(image, watermark_layer)
        
        # 转换为base64
        result_base64 = processor.image_to_base64(result_image, output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "成功添加水印",
                "data": {
                    "image_data": result_base64,
                    "metadata": {
                        "size": f"{image.width}x{image.height}",
                        "watermark_type": "text" if watermark_text else "image",
                        "position": position,
                        "opacity": opacity,
                        "scale": scale,
                        "format": output_format
                    }
                }
            }, ensure_ascii=False)
        )]
        
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"参数验证失败: {str(e)}"
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"添加水印失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def apply_vignette(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    为图片添加暗角效果
    
    Args:
        arguments: 包含图片源和暗角参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        intensity = arguments.get("intensity", 0.5)
        radius = arguments.get("radius", 0.7)
        color = arguments.get("color", "#000000")
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(intensity, 0.0, 1.0, "intensity")
        validate_numeric_range(radius, 0.0, 1.0, "radius")
        validate_color_hex(color)
        
        # 加载图片
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 转换为RGBA模式
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # 创建暗角遮罩
        mask = Image.new("L", image.size, 255)
        draw = ImageDraw.Draw(mask)
        
        # 计算中心点和半径
        center_x, center_y = image.width // 2, image.height // 2
        max_radius = min(image.width, image.height) // 2
        vignette_radius = int(max_radius * radius)
        
        # 创建径向渐变
        for y in range(image.height):
            for x in range(image.width):
                # 计算到中心的距离
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                
                # 计算暗角强度
                if distance <= vignette_radius:
                    alpha = 255
                else:
                    # 在半径外应用渐变
                    fade_distance = distance - vignette_radius
                    fade_ratio = min(fade_distance / (max_radius - vignette_radius), 1.0)
                    alpha = int(255 * (1 - intensity * fade_ratio))
                
                mask.putpixel((x, y), alpha)
        
        # 应用高斯模糊使暗角更自然
        mask = mask.filter(ImageFilter.GaussianBlur(radius=max_radius * 0.1))
        
        # 创建暗角图层
        vignette_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        vignette_layer = Image.new("RGBA", image.size, vignette_rgb + (0,))
        
        # 应用遮罩
        vignette_layer.putalpha(mask)
        
        # 合成图片
        result_image = Image.alpha_composite(image, vignette_layer)
        
        # 转换为base64
        result_base64 = processor.image_to_base64(result_image, output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "成功添加暗角效果",
                "data": {
                    "image_data": result_base64,
                    "metadata": {
                        "size": f"{image.width}x{image.height}",
                        "intensity": intensity,
                        "radius": radius,
                        "color": color,
                        "format": output_format
                    }
                }
            }, ensure_ascii=False)
        )]
        
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"参数验证失败: {str(e)}"
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"添加暗角效果失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def create_polaroid(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    创建宝丽来照片效果
    
    Args:
        arguments: 包含图片源和宝丽来参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        border_width = arguments.get("border_width", 40)
        bottom_border = arguments.get("bottom_border", 80)
        border_color = arguments.get("border_color", "#FFFFFF")
        rotation = arguments.get("rotation", 0)
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(border_width, 10, 100, "border_width")
        validate_numeric_range(bottom_border, 20, 200, "bottom_border")
        validate_color_hex(border_color)
        validate_numeric_range(rotation, -15, 15, "rotation")
        
        # 加载图片
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 创建宝丽来边框
        polaroid_width = image.width + 2 * border_width
        polaroid_height = image.height + border_width + bottom_border
        
        # 创建白色背景
        border_rgb = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
        polaroid = Image.new("RGB", (polaroid_width, polaroid_height), border_rgb)
        
        # 粘贴原图片
        polaroid.paste(image, (border_width, border_width))
        
        # 应用旋转
        if rotation != 0:
            # 扩展画布以容纳旋转后的图片
            diagonal = int(((polaroid_width ** 2 + polaroid_height ** 2) ** 0.5))
            expanded = Image.new("RGBA", (diagonal, diagonal), (0, 0, 0, 0))
            
            # 将宝丽来图片粘贴到扩展画布的中心
            offset_x = (diagonal - polaroid_width) // 2
            offset_y = (diagonal - polaroid_height) // 2
            expanded.paste(polaroid, (offset_x, offset_y))
            
            # 旋转
            rotated = expanded.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
            
            # 裁剪到合适大小
            bbox = rotated.getbbox()
            if bbox:
                polaroid = rotated.crop(bbox)
        
        # 添加轻微的阴影效果
        shadow_offset = 5
        shadow_size = (polaroid.width + shadow_offset * 2, polaroid.height + shadow_offset * 2)
        final_image = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
        
        # 创建阴影
        shadow = Image.new("RGBA", polaroid.size, (128, 128, 128, 100))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=3))
        final_image.paste(shadow, (shadow_offset, shadow_offset), shadow)
        
        # 粘贴宝丽来图片
        if polaroid.mode != "RGBA":
            polaroid = polaroid.convert("RGBA")
        final_image.paste(polaroid, (0, 0), polaroid)
        
        # 转换为base64
        result_base64 = processor.image_to_base64(final_image, output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "成功创建宝丽来效果",
                "data": {
                    "image_data": result_base64,
                    "metadata": {
                        "original_size": f"{image.width}x{image.height}",
                        "polaroid_size": f"{final_image.width}x{final_image.height}",
                        "border_width": border_width,
                        "bottom_border": bottom_border,
                        "border_color": border_color,
                        "rotation": rotation,
                        "format": output_format
                    }
                }
            }, ensure_ascii=False)
        )]
        
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"参数验证失败: {str(e)}"
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"创建宝丽来效果失败: {str(e)}"
            }, ensure_ascii=False)
        )]