"""
基础操作工具
包含图片加载、保存、格式转换等基础功能
"""

from mcp.types import Tool
from typing import List

def get_basic_tools() -> List[Tool]:
    """返回基础操作工具列表"""
    return [
        Tool(
            name="load_image",
            description="加载图片文件或base64编码的图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "图片源：文件路径或base64编码字符串"
                    }
                },
                "required": ["source"]
            }
        ),
        Tool(
            name="save_image",
            description="保存图片到指定路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出文件路径"
                    },
                    "format": {
                        "type": "string",
                        "description": "图片格式（PNG, JPEG, BMP等）",
                        "default": "PNG"
                    },
                    "quality": {
                        "type": "integer",
                        "description": "图片质量（1-100，仅对JPEG有效）",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 95
                    }
                },
                "required": ["image_data", "output_path"]
            }
        ),
        Tool(
            name="get_image_info",
            description="获取图片基本信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    }
                },
                "required": ["image_data"]
            }
        ),
        Tool(
            name="convert_format",
            description="转换图片格式",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "target_format": {
                        "type": "string",
                        "description": "目标格式（PNG, JPEG, BMP, TIFF, WEBP）"
                    },
                    "quality": {
                        "type": "integer",
                        "description": "图片质量（1-100，仅对JPEG有效）",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 95
                    }
                },
                "required": ["image_data", "target_format"]
            }
        )
    ]

from utils.image_processor import ImageProcessor
from utils.validation import ensure_valid_image_source, validate_image_format, ValidationError
from mcp.types import TextContent
import json
import os

# 全局图片处理器实例
processor = ImageProcessor()

async def load_image(source: str) -> list[TextContent]:
    """
    加载图片
    
    Args:
        source: 图片源（文件路径或base64编码）
        
    Returns:
        包含图片信息和base64数据的响应
    """
    try:
        # 验证图片源
        ensure_valid_image_source(source)
        
        # 加载图片
        image = processor.load_image(source)
        
        # 获取图片信息
        info = processor.get_image_info(image)
        
        # 转换为base64
        base64_data = processor.image_to_base64(image)
        
        result = {
            "success": True,
            "message": "图片加载成功",
            "data": {
                "image_data": base64_data,
                "info": info
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        
    except ValidationError as e:
        error_result = {
            "success": False,
            "error": f"参数验证失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"图片加载失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def save_image(image_data: str, output_path: str, format: str = "PNG", quality: int = 95) -> list[TextContent]:
    """
    保存图片到指定路径
    
    Args:
        image_data: 图片数据（base64编码）
        output_path: 输出文件路径
        format: 图片格式
        quality: 图片质量
        
    Returns:
        保存结果响应
    """
    try:
        # 验证参数
        if not image_data or not output_path:
            raise ValidationError("图片数据和输出路径不能为空")
        
        if not validate_image_format(format):
            raise ValidationError(f"不支持的图片格式: {format}")
        
        if not (1 <= quality <= 100):
            raise ValidationError("图片质量必须在1-100之间")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 保存图片
        saved_path = processor.save_image(image, output_path, format, quality)
        
        # 获取文件信息
        file_size = os.path.getsize(saved_path)
        
        result = {
            "success": True,
            "message": "图片保存成功",
            "data": {
                "output_path": saved_path,
                "format": format,
                "file_size": file_size,
                "quality": quality
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        
    except ValidationError as e:
        error_result = {
            "success": False,
            "error": f"参数验证失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"图片保存失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def get_image_info(image_source: str) -> list[TextContent]:
    """
    获取图片信息
    
    Args:
        image_source: 图片源（文件路径或base64编码数据）
        
    Returns:
        图片信息响应
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片源不能为空")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 获取详细信息
        info = processor.get_image_info(image)
        
        # 计算图片大小（字节）
        import io
        buffer = io.BytesIO()
        image.save(buffer, format=image.format or 'PNG')
        data_size = len(buffer.getvalue())
        
        # 扩展信息
        extended_info = {
            **info,
            "data_size": data_size,
            "aspect_ratio": round(info['width'] / info['height'], 2),
            "total_pixels": info['width'] * info['height']
        }
        
        # 如果是文件路径，添加文件信息
        if not image_source.startswith('data:image') and os.path.exists(image_source):
            extended_info["file_path"] = image_source
            extended_info["file_size_bytes"] = os.path.getsize(image_source)
        
        result = {
            "success": True,
            "message": "获取图片信息成功",
            "data": extended_info
        }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        
    except ValidationError as e:
        error_result = {
            "success": False,
            "error": f"参数验证失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"获取图片信息失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def convert_format(image_source: str, target_format: str, quality: int = 95) -> list[TextContent]:
    """
    转换图片格式
    
    Args:
        image_source: 图片源（文件路径或base64编码数据）
        target_format: 目标格式
        quality: 图片质量
        
    Returns:
        转换后的图片数据
    """
    try:
        # 验证参数
        if not image_source or not target_format:
            raise ValidationError("图片源和目标格式不能为空")
        
        if not validate_image_format(target_format):
            raise ValidationError(f"不支持的目标格式: {target_format}")
        
        if not (1 <= quality <= 100):
            raise ValidationError("图片质量必须在1-100之间")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 获取原始格式
        original_format = image.format or 'PNG'
        
        # 转换格式
        converted_data = processor.image_to_base64(image, target_format)
        
        result = {
            "success": True,
            "message": f"图片格式转换成功: {original_format} -> {target_format}",
            "data": {
                "image_data": converted_data,
                "original_format": original_format,
                "target_format": target_format,
                "quality": quality
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        
    except ValidationError as e:
        error_result = {
            "success": False,
            "error": f"参数验证失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"格式转换失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]