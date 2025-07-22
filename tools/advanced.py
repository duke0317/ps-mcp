"""
高级功能模块

提供批量操作、图片合成、缩略图生成等高级图片处理功能。
"""

from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import json
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
import time

from mcp.types import Tool, TextContent

from utils.image_processor import ImageProcessor
from utils.validation import (
    validate_image_source, validate_numeric_range, validate_color_hex,
    ensure_valid_image_source, ValidationError
)
from config import (
    MAX_IMAGE_SIZE, MIN_IMAGE_SIZE, MIN_DIMENSION, MAX_BLUR_RADIUS,
    DEFAULT_FORMAT, DEFAULT_QUALITY, DEFAULT_IMAGE_FORMAT
)

def get_advanced_tools() -> List[Tool]:
    """
    返回高级功能工具列表
    
    Returns:
        List[Tool]: 高级功能工具列表
    """
    return [
        Tool(
            name="batch_resize",
            description="批量调整多张图片的大小",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_sources": {
                        "type": "array",
                        "description": "图片源列表（文件路径或base64编码）",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 10
                    },
                    "width": {
                        "type": "integer",
                        "description": "目标宽度",
                        "minimum": MIN_IMAGE_SIZE,
                        "maximum": MAX_IMAGE_SIZE
                    },
                    "height": {
                        "type": "integer",
                        "description": "目标高度",
                        "minimum": MIN_IMAGE_SIZE,
                        "maximum": MAX_IMAGE_SIZE
                    },
                    "maintain_aspect_ratio": {
                        "type": "boolean",
                        "description": "是否保持宽高比",
                        "default": True
                    },
                    "resample_method": {
                        "type": "string",
                        "description": "重采样方法",
                        "enum": ["LANCZOS", "BILINEAR", "BICUBIC", "NEAREST"],
                        "default": "LANCZOS"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_sources", "width", "height"]
            }
        ),
        Tool(
            name="create_collage",
            description="创建图片拼贴",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_sources": {
                        "type": "array",
                        "description": "图片源列表（文件路径或base64编码）",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 9
                    },
                    "layout": {
                        "type": "string",
                        "description": "拼贴布局",
                        "enum": ["grid", "horizontal", "vertical", "mosaic"],
                        "default": "grid"
                    },
                    "spacing": {
                        "type": "integer",
                        "description": "图片间距（像素）",
                        "minimum": 0,
                        "maximum": 50,
                        "default": 10
                    },
                    "background_color": {
                        "type": "string",
                        "description": "背景颜色（十六进制格式）",
                        "default": "#FFFFFF"
                    },
                    "max_width": {
                        "type": "integer",
                        "description": "最大宽度",
                        "minimum": 200,
                        "maximum": MAX_IMAGE_SIZE,
                        "default": 1200
                    },
                    "max_height": {
                        "type": "integer",
                        "description": "最大高度",
                        "minimum": 200,
                        "maximum": MAX_IMAGE_SIZE,
                        "default": 1200
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_sources"]
            }
        ),
        Tool(
            name="create_thumbnail_grid",
            description="创建缩略图网格",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_sources": {
                        "type": "array",
                        "description": "图片源列表（文件路径或base64编码）",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 20
                    },
                    "thumbnail_size": {
                        "type": "integer",
                        "description": "缩略图大小（像素）",
                        "minimum": 50,
                        "maximum": 300,
                        "default": 150
                    },
                    "columns": {
                        "type": "integer",
                        "description": "列数",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 4
                    },
                    "spacing": {
                        "type": "integer",
                        "description": "间距（像素）",
                        "minimum": 0,
                        "maximum": 50,
                        "default": 10
                    },
                    "background_color": {
                        "type": "string",
                        "description": "背景颜色（十六进制格式）",
                        "default": "#FFFFFF"
                    },
                    "border_width": {
                        "type": "integer",
                        "description": "边框宽度",
                        "minimum": 0,
                        "maximum": 10,
                        "default": 2
                    },
                    "border_color": {
                        "type": "string",
                        "description": "边框颜色（十六进制格式）",
                        "default": "#CCCCCC"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image_sources"]
            }
        ),
        Tool(
            name="blend_images",
            description="混合两张图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "image1_source": {
                        "type": "string",
                        "description": "第一张图片源（文件路径或base64编码）"
                    },
                    "image2_source": {
                        "type": "string",
                        "description": "第二张图片源（文件路径或base64编码）"
                    },
                    "blend_mode": {
                        "type": "string",
                        "description": "混合模式",
                        "enum": ["normal", "multiply", "screen", "overlay", "soft_light", "hard_light"],
                        "default": "normal"
                    },
                    "opacity": {
                        "type": "number",
                        "description": "第二张图片的透明度（0.0-1.0）",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    },
                    "resize_mode": {
                        "type": "string",
                        "description": "尺寸调整模式",
                        "enum": ["fit_first", "fit_second", "fit_largest", "fit_smallest"],
                        "default": "fit_first"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["PNG", "JPEG", "WEBP"],
                        "default": "PNG"
                    }
                },
                "required": ["image1_source", "image2_source"]
            }
        ),
        Tool(
            name="extract_colors",
            description="提取图片的主要颜色",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片源（文件路径或base64编码）"
                    },
                    "color_count": {
                        "type": "integer",
                        "description": "提取的颜色数量",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5
                    },
                    "create_palette": {
                        "type": "boolean",
                        "description": "是否创建调色板图片",
                        "default": True
                    },
                    "palette_width": {
                        "type": "integer",
                        "description": "调色板宽度",
                        "minimum": 100,
                        "maximum": 800,
                        "default": 400
                    },
                    "palette_height": {
                        "type": "integer",
                        "description": "调色板高度",
                        "minimum": 50,
                        "maximum": 200,
                        "default": 100
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="create_gif",
            description="从多张图片创建GIF动画",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_sources": {
                        "type": "array",
                        "description": "图片源列表（文件路径或base64编码）",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 20
                    },
                    "duration": {
                        "type": "integer",
                        "description": "每帧持续时间（毫秒）",
                        "minimum": 100,
                        "maximum": 5000,
                        "default": 500
                    },
                    "loop": {
                        "type": "boolean",
                        "description": "是否循环播放",
                        "default": True
                    },
                    "optimize": {
                        "type": "boolean",
                        "description": "是否优化文件大小",
                        "default": True
                    },
                    "resize_to": {
                        "type": "object",
                        "description": "调整所有帧到指定尺寸",
                        "properties": {
                            "width": {"type": "integer", "minimum": 50, "maximum": 800},
                            "height": {"type": "integer", "minimum": 50, "maximum": 800}
                        }
                    }
                },
                "required": ["image_sources"]
            }
        )
    ]

# 高级功能实现

async def batch_resize(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    批量调整多张图片的大小
    
    Args:
        arguments: 包含图片源列表和调整参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_sources = arguments.get("image_sources", [])
        if not image_sources:
            raise ValidationError("image_sources不能为空")
        
        width = arguments.get("width")
        height = arguments.get("height")
        maintain_aspect_ratio = arguments.get("maintain_aspect_ratio", True)
        resample_method = arguments.get("resample_method", "LANCZOS")
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(width, MIN_IMAGE_SIZE, MAX_IMAGE_SIZE, "width")
        validate_numeric_range(height, MIN_IMAGE_SIZE, MAX_IMAGE_SIZE, "height")
        
        # 获取重采样方法
        resample_map = {
            "LANCZOS": Image.Resampling.LANCZOS,
            "BILINEAR": Image.Resampling.BILINEAR,
            "BICUBIC": Image.Resampling.BICUBIC,
            "NEAREST": Image.Resampling.NEAREST
        }
        resample = resample_map.get(resample_method, Image.Resampling.LANCZOS)
        
        processor = ImageProcessor()
        results = []
        failed_count = 0
        
        # 使用线程池进行并行处理
        def resize_single_image(image_source):
            try:
                ensure_valid_image_source(image_source)
                image = processor.load_image(image_source)
                
                if maintain_aspect_ratio:
                    # 保持宽高比
                    image.thumbnail((width, height), resample)
                    resized_image = image
                else:
                    # 强制调整到指定尺寸
                    resized_image = image.resize((width, height), resample)
                
                # 输出图片
                output_info = processor.output_image(resized_image, "batch_resize", output_format)
                return output_info
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        # 并行处理
        with ThreadPoolExecutor(max_workers=min(len(image_sources), MAX_CONCURRENT_TASKS)) as executor:
            futures = [executor.submit(resize_single_image, source) for source in image_sources]
            
            for i, future in enumerate(futures):
                result = future.result()
                if result.startswith("ERROR:"):
                    failed_count += 1
                    results.append({
                        "index": i,
                        "success": False,
                        "error": result[7:]  # 移除"ERROR: "前缀
                    })
                else:
                    results.append({
                        "index": i,
                        "success": True,
                        "result": result
                    })
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"批量调整完成，成功: {len(results) - failed_count}, 失败: {failed_count}",
                "results": results,
                "metadata": {
                    "total_images": len(image_sources),
                    "successful": len(results) - failed_count,
                    "failed": failed_count,
                    "target_size": f"{width}x{height}",
                    "maintain_aspect_ratio": maintain_aspect_ratio,
                    "resample_method": resample_method,
                    "format": output_format
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
                "error": f"批量调整失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def create_collage(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    创建图片拼贴
    
    Args:
        arguments: 包含图片源列表和拼贴参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_sources = arguments.get("image_sources", [])
        if len(image_sources) < 2:
            raise ValidationError("至少需要2张图片")
        
        layout = arguments.get("layout", "grid")
        spacing = arguments.get("spacing", 10)
        background_color = arguments.get("background_color", "#FFFFFF")
        max_width = arguments.get("max_width", 1200)
        max_height = arguments.get("max_height", 1200)
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(spacing, 0, 50, "spacing")
        validate_color_hex(background_color)
        validate_numeric_range(max_width, 200, MAX_IMAGE_SIZE, "max_width")
        validate_numeric_range(max_height, 200, MAX_IMAGE_SIZE, "max_height")
        
        processor = ImageProcessor()
        images = []
        
        # 加载所有图片
        for source in image_sources:
            ensure_valid_image_source(source)
            image = processor.load_image(source)
            images.append(image)
        
        # 根据布局创建拼贴
        if layout == "horizontal":
            # 水平排列
            total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
            max_height_img = max(img.height for img in images)
            
            # 缩放以适应最大尺寸
            if total_width > max_width:
                scale = max_width / total_width
                images = [img.resize((int(img.width * scale), int(img.height * scale)), 
                                   Image.Resampling.LANCZOS) for img in images]
                total_width = max_width
                max_height_img = max(img.height for img in images)
            
            collage = Image.new("RGB", (total_width, max_height_img), background_color)
            x_offset = 0
            
            for img in images:
                y_offset = (max_height_img - img.height) // 2
                collage.paste(img, (x_offset, y_offset))
                x_offset += img.width + spacing
                
        elif layout == "vertical":
            # 垂直排列
            max_width_img = max(img.width for img in images)
            total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
            
            # 缩放以适应最大尺寸
            if total_height > max_height:
                scale = max_height / total_height
                images = [img.resize((int(img.width * scale), int(img.height * scale)), 
                                   Image.Resampling.LANCZOS) for img in images]
                max_width_img = max(img.width for img in images)
                total_height = max_height
            
            collage = Image.new("RGB", (max_width_img, total_height), background_color)
            y_offset = 0
            
            for img in images:
                x_offset = (max_width_img - img.width) // 2
                collage.paste(img, (x_offset, y_offset))
                y_offset += img.height + spacing
                
        else:  # grid 或 mosaic
            # 网格排列
            import math
            cols = math.ceil(math.sqrt(len(images)))
            rows = math.ceil(len(images) / cols)
            
            # 计算每个单元格的大小
            cell_width = (max_width - spacing * (cols - 1)) // cols
            cell_height = (max_height - spacing * (rows - 1)) // rows
            
            # 调整所有图片到单元格大小
            resized_images = []
            for img in images:
                img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)
                resized_images.append(img)
            
            # 创建拼贴
            collage_width = cols * cell_width + spacing * (cols - 1)
            collage_height = rows * cell_height + spacing * (rows - 1)
            collage = Image.new("RGB", (collage_width, collage_height), background_color)
            
            for i, img in enumerate(resized_images):
                row = i // cols
                col = i % cols
                
                x = col * (cell_width + spacing)
                y = row * (cell_height + spacing)
                
                # 居中放置图片
                x_offset = x + (cell_width - img.width) // 2
                y_offset = y + (cell_height - img.height) // 2
                
                collage.paste(img, (x_offset, y_offset))
        
        # 转换为base64
        output_info = processor.output_image(collage, "batch_resize", output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"成功创建{layout}拼贴",
                "data": {
                    **output_info,
                    "metadata": {
                        "image_count": len(images),
                        "layout": layout,
                        "size": f"{collage.width}x{collage.height}",
                        "spacing": spacing,
                        "background_color": background_color,
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
                "error": f"创建拼贴失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def create_thumbnail_grid(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    创建缩略图网格
    
    Args:
        arguments: 包含图片源列表和网格参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_sources = arguments.get("image_sources", [])
        if not image_sources:
            raise ValidationError("image_sources不能为空")
        
        thumbnail_size = arguments.get("thumbnail_size", 150)
        columns = arguments.get("columns", 4)
        spacing = arguments.get("spacing", 10)
        background_color = arguments.get("background_color", "#FFFFFF")
        border_width = arguments.get("border_width", 2)
        border_color = arguments.get("border_color", "#CCCCCC")
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(thumbnail_size, 50, 300, "thumbnail_size")
        validate_numeric_range(columns, 1, 10, "columns")
        validate_numeric_range(spacing, 0, 50, "spacing")
        validate_color_hex(background_color)
        validate_numeric_range(border_width, 0, 10, "border_width")
        validate_color_hex(border_color)
        
        processor = ImageProcessor()
        thumbnails = []
        
        # 创建缩略图
        for source in image_sources:
            try:
                ensure_valid_image_source(source)
                image = processor.load_image(source)
                
                # 创建正方形缩略图
                image.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
                
                # 创建正方形背景
                thumb = Image.new("RGB", (thumbnail_size, thumbnail_size), background_color)
                
                # 居中粘贴图片
                x_offset = (thumbnail_size - image.width) // 2
                y_offset = (thumbnail_size - image.height) // 2
                thumb.paste(image, (x_offset, y_offset))
                
                # 添加边框
                if border_width > 0:
                    draw = ImageDraw.Draw(thumb)
                    for i in range(border_width):
                        draw.rectangle(
                            [i, i, thumbnail_size - 1 - i, thumbnail_size - 1 - i],
                            outline=border_color
                        )
                
                thumbnails.append(thumb)
                
            except Exception as e:
                # 创建错误占位符
                error_thumb = Image.new("RGB", (thumbnail_size, thumbnail_size), "#FF0000")
                draw = ImageDraw.Draw(error_thumb)
                draw.text((10, thumbnail_size//2), "ERROR", fill="white")
                thumbnails.append(error_thumb)
        
        # 计算网格尺寸
        rows = (len(thumbnails) + columns - 1) // columns
        grid_width = columns * thumbnail_size + spacing * (columns - 1)
        grid_height = rows * thumbnail_size + spacing * (rows - 1)
        
        # 创建网格
        grid = Image.new("RGB", (grid_width, grid_height), background_color)
        
        for i, thumb in enumerate(thumbnails):
            row = i // columns
            col = i % columns
            
            x = col * (thumbnail_size + spacing)
            y = row * (thumbnail_size + spacing)
            
            grid.paste(thumb, (x, y))
        
        # 转换为base64
        output_info = processor.output_image(grid, "batch_resize", output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"成功创建{len(thumbnails)}个缩略图的网格",
                "data": {
                    **output_info,
                    "metadata": {
                        "thumbnail_count": len(thumbnails),
                        "grid_size": f"{grid.width}x{grid.height}",
                        "thumbnail_size": thumbnail_size,
                        "columns": columns,
                        "rows": rows,
                        "spacing": spacing,
                        "border_width": border_width,
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
                "error": f"创建缩略图网格失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def blend_images(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    混合两张图片
    
    Args:
        arguments: 包含两张图片源和混合参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image1_source = arguments.get("image1_source")
        image2_source = arguments.get("image2_source")
        ensure_valid_image_source(image1_source)
        ensure_valid_image_source(image2_source)
        
        blend_mode = arguments.get("blend_mode", "normal")
        opacity = arguments.get("opacity", 0.5)
        resize_mode = arguments.get("resize_mode", "fit_first")
        output_format = arguments.get("output_format", DEFAULT_IMAGE_FORMAT)
        
        # 验证参数
        validate_numeric_range(opacity, 0.0, 1.0, "opacity")
        
        processor = ImageProcessor()
        
        # 加载图片
        image1 = processor.load_image(image1_source)
        image2 = processor.load_image(image2_source)
        
        # 转换为RGBA模式
        if image1.mode != "RGBA":
            image1 = image1.convert("RGBA")
        if image2.mode != "RGBA":
            image2 = image2.convert("RGBA")
        
        # 调整尺寸
        if resize_mode == "fit_first":
            image2 = image2.resize(image1.size, Image.Resampling.LANCZOS)
            final_size = image1.size
        elif resize_mode == "fit_second":
            image1 = image1.resize(image2.size, Image.Resampling.LANCZOS)
            final_size = image2.size
        elif resize_mode == "fit_largest":
            if image1.width * image1.height > image2.width * image2.height:
                image2 = image2.resize(image1.size, Image.Resampling.LANCZOS)
                final_size = image1.size
            else:
                image1 = image1.resize(image2.size, Image.Resampling.LANCZOS)
                final_size = image2.size
        else:  # fit_smallest
            if image1.width * image1.height < image2.width * image2.height:
                image2 = image2.resize(image1.size, Image.Resampling.LANCZOS)
                final_size = image1.size
            else:
                image1 = image1.resize(image2.size, Image.Resampling.LANCZOS)
                final_size = image2.size
        
        # 调整第二张图片的透明度
        alpha_channel = image2.split()[-1]
        alpha_channel = alpha_channel.point(lambda p: int(p * opacity))
        image2.putalpha(alpha_channel)
        
        # 应用混合模式
        if blend_mode == "normal":
            result = Image.alpha_composite(image1, image2)
        elif blend_mode == "multiply":
            # 简化的乘法混合
            result = Image.blend(image1, image2, opacity)
        elif blend_mode == "screen":
            # 简化的屏幕混合
            result = Image.blend(image1, image2, opacity)
        else:
            # 其他混合模式使用普通混合
            result = Image.alpha_composite(image1, image2)
        
        # 转换为base64
        output_info = processor.output_image(result, "batch_resize", output_format)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"成功混合图片，使用{blend_mode}模式",
                "data": {
                    **output_info,
                    "metadata": {
                        "size": f"{result.width}x{result.height}",
                        "blend_mode": blend_mode,
                        "opacity": opacity,
                        "resize_mode": resize_mode,
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
                "error": f"混合图片失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def extract_colors(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    提取图片的主要颜色
    
    Args:
        arguments: 包含图片源和颜色提取参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_source = arguments.get("image_source")
        ensure_valid_image_source(image_source)
        
        color_count = arguments.get("color_count") or arguments.get("num_colors", 5)
        create_palette = arguments.get("create_palette", True)
        palette_width = arguments.get("palette_width", 400)
        palette_height = arguments.get("palette_height", 100)
        
        # 验证参数
        validate_numeric_range(color_count, 1, 20, "color_count")
        validate_numeric_range(palette_width, 100, 800, "palette_width")
        validate_numeric_range(palette_height, 50, 200, "palette_height")
        
        processor = ImageProcessor()
        image = processor.load_image(image_source)
        
        # 转换为RGB模式
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # 使用量化来提取主要颜色
        quantized = image.quantize(colors=color_count)
        palette_colors = quantized.getpalette()
        
        # 提取RGB颜色值
        colors = []
        # 确保不超过实际可用的颜色数量
        actual_color_count = min(color_count, len(palette_colors) // 3)
        
        for i in range(actual_color_count):
            try:
                r = palette_colors[i * 3]
                g = palette_colors[i * 3 + 1] 
                b = palette_colors[i * 3 + 2]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append({
                    "rgb": [r, g, b],
                    "hex": hex_color
                })
            except IndexError:
                # 如果索引越界，停止添加颜色
                break
        
        result_data = {
            "success": True,
            "message": f"成功提取{len(colors)}种主要颜色",
            "colors": colors,
            "metadata": {
                "image_size": f"{image.width}x{image.height}",
                "color_count": len(colors)
            }
        }
        
        # 创建调色板图片
        if create_palette:
            palette_image = Image.new("RGB", (palette_width, palette_height))
            color_width = palette_width // len(colors)
            
            for i, color_info in enumerate(colors):
                color_rgb = tuple(color_info["rgb"])
                x1 = i * color_width
                x2 = (i + 1) * color_width if i < len(colors) - 1 else palette_width
                
                # 填充颜色块
                for x in range(x1, x2):
                    for y in range(palette_height):
                        palette_image.putpixel((x, y), color_rgb)
            
            # 输出调色板图片
            palette_output = processor.output_image(palette_image, "extract_colors", "PNG")
            result_data["palette"] = palette_output
            result_data["metadata"]["palette_size"] = f"{palette_width}x{palette_height}"
        
        return [TextContent(
            type="text",
            text=json.dumps(result_data, ensure_ascii=False)
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
                "error": f"提取颜色失败: {str(e)}"
            }, ensure_ascii=False)
        )]

async def create_gif(arguments: Dict[str, Any]) -> List[TextContent]:
    """
    从多张图片创建GIF动画
    
    Args:
        arguments: 包含图片源列表和GIF参数的字典
        
    Returns:
        List[TextContent]: 处理结果
    """
    try:
        # 参数验证
        image_sources = arguments.get("image_sources", [])
        if len(image_sources) < 2:
            raise ValidationError("至少需要2张图片")
        
        duration = arguments.get("duration", 500)
        loop = arguments.get("loop", True)
        optimize = arguments.get("optimize", True)
        resize_to = arguments.get("resize_to")
        
        # 验证参数
        validate_numeric_range(duration, 100, 5000, "duration")
        
        processor = ImageProcessor()
        frames = []
        
        # 加载所有图片
        for source in image_sources:
            ensure_valid_image_source(source)
            image = processor.load_image(source)
            
            # 转换为RGB模式（GIF不支持RGBA）
            if image.mode != "RGB":
                if image.mode == "RGBA":
                    # 创建白色背景
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    image = image.convert("RGB")
            
            frames.append(image)
        
        # 调整所有帧到相同尺寸
        if resize_to:
            target_width = resize_to.get("width")
            target_height = resize_to.get("height")
            if target_width and target_height:
                frames = [frame.resize((target_width, target_height), Image.Resampling.LANCZOS) 
                         for frame in frames]
        else:
            # 使用第一帧的尺寸
            target_size = frames[0].size
            frames = [frame.resize(target_size, Image.Resampling.LANCZOS) for frame in frames]
        
        # 创建GIF
        import io
        gif_buffer = io.BytesIO()
        
        frames[0].save(
            gif_buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0 if loop else 1,
            optimize=optimize
        )
        
        # 转换为base64
        gif_buffer.seek(0)
        gif_data = gif_buffer.getvalue()
        gif_base64 = f"data:image/gif;base64,{processor._bytes_to_base64(gif_data)}"
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"成功创建包含{len(frames)}帧的GIF动画",
                "result": gif_base64,
                "metadata": {
                    "frame_count": len(frames),
                    "size": f"{frames[0].width}x{frames[0].height}",
                    "duration": duration,
                    "loop": loop,
                    "optimize": optimize,
                    "file_size": len(gif_data)
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
                "error": f"创建GIF失败: {str(e)}"
            }, ensure_ascii=False)
        )]