"""
几何变换工具
包含缩放、裁剪、旋转等几何变换功能
"""

from mcp.types import Tool
from typing import List

def get_transform_tools() -> List[Tool]:
    """返回几何变换工具列表"""
    return [
        Tool(
            name="resize_image",
            description="调整图片大小",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "width": {
                        "type": "integer",
                        "description": "目标宽度",
                        "minimum": 1,
                        "maximum": 4096
                    },
                    "height": {
                        "type": "integer",
                        "description": "目标高度",
                        "minimum": 1,
                        "maximum": 4096
                    },
                    "keep_aspect_ratio": {
                        "type": "boolean",
                        "description": "是否保持宽高比",
                        "default": True
                    },
                    "resample": {
                        "type": "string",
                        "description": "重采样方法（NEAREST, BILINEAR, BICUBIC, LANCZOS）",
                        "default": "LANCZOS"
                    }
                },
                "required": ["image_data", "width", "height"]
            }
        ),
        Tool(
            name="crop_image",
            description="裁剪图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "left": {
                        "type": "integer",
                        "description": "左边界坐标",
                        "minimum": 0
                    },
                    "top": {
                        "type": "integer",
                        "description": "上边界坐标",
                        "minimum": 0
                    },
                    "right": {
                        "type": "integer",
                        "description": "右边界坐标"
                    },
                    "bottom": {
                        "type": "integer",
                        "description": "下边界坐标"
                    }
                },
                "required": ["image_data", "left", "top", "right", "bottom"]
            }
        ),
        Tool(
            name="rotate_image",
            description="旋转图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "angle": {
                        "type": "number",
                        "description": "旋转角度（度，正值为顺时针）"
                    },
                    "expand": {
                        "type": "boolean",
                        "description": "是否扩展画布以容纳旋转后的图片",
                        "default": True
                    },
                    "fill_color": {
                        "type": "string",
                        "description": "填充颜色（十六进制格式，如#FFFFFF）",
                        "default": "#FFFFFF"
                    }
                },
                "required": ["image_data", "angle"]
            }
        ),
        Tool(
            name="flip_image",
            description="翻转图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "direction": {
                        "type": "string",
                        "description": "翻转方向（horizontal, vertical）",
                        "enum": ["horizontal", "vertical"]
                    }
                },
                "required": ["image_data", "direction"]
            }
        )
    ]

from utils.image_processor import ImageProcessor
from utils.validation import ensure_valid_dimensions, validate_crop_coordinates, validate_color_hex, ValidationError
from mcp.types import TextContent
from PIL import Image
import json

# 全局图片处理器实例
processor = ImageProcessor()

async def resize_image(image_source: str, width: int, height: int, 
                      keep_aspect_ratio: bool = True, resample: str = "LANCZOS") -> list[TextContent]:
    """
    调整图片大小
    
    Args:
        image_source: 图片源（文件路径或base64编码数据）
        width: 目标宽度
        height: 目标高度
        keep_aspect_ratio: 是否保持宽高比
        resample: 重采样方法
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片源不能为空")
        
        ensure_valid_dimensions(width, height)
        
        # 验证重采样方法
        resample_methods = {
            'NEAREST': Image.NEAREST,
            'BILINEAR': Image.BILINEAR,
            'BICUBIC': Image.BICUBIC,
            'LANCZOS': Image.LANCZOS
        }
        
        if resample.upper() not in resample_methods:
            raise ValidationError(f"不支持的重采样方法: {resample}")
        
        # 加载图片
        image = processor.load_image(image_source)
        original_size = image.size
        
        # 计算目标尺寸
        if keep_aspect_ratio:
            # 保持宽高比，计算实际尺寸
            aspect_ratio = original_size[0] / original_size[1]
            target_aspect_ratio = width / height
            
            if aspect_ratio > target_aspect_ratio:
                # 以宽度为准
                new_width = width
                new_height = int(width / aspect_ratio)
            else:
                # 以高度为准
                new_height = height
                new_width = int(height * aspect_ratio)
        else:
            new_width, new_height = width, height
        
        # 调整大小
        resized_image = image.resize(
            (new_width, new_height), 
            resample_methods[resample.upper()]
        )
        
        # 转换为base64
        result_data = processor.image_to_base64(resized_image)
        
        result = {
            "success": True,
            "message": f"图片大小调整成功: {original_size} -> {(new_width, new_height)}",
            "data": {
                "image_data": result_data,
                "original_size": original_size,
                "new_size": (new_width, new_height),
                "keep_aspect_ratio": keep_aspect_ratio,
                "resample_method": resample
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
            "error": f"图片大小调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def crop_image(image_data: str, left: int, top: int, right: int, bottom: int) -> list[TextContent]:
    """
    裁剪图片
    
    Args:
        image_data: 图片数据（base64编码）
        left, top, right, bottom: 裁剪坐标
        
    Returns:
        裁剪后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        image_width, image_height = image.size
        
        # 验证裁剪坐标
        if not validate_crop_coordinates(left, top, right, bottom, image_width, image_height):
            raise ValidationError(f"无效的裁剪坐标: ({left}, {top}, {right}, {bottom}), 图片尺寸: {image_width}x{image_height}")
        
        # 裁剪图片
        cropped_image = image.crop((left, top, right, bottom))
        
        # 转换为base64
        result_data = processor.image_to_base64(cropped_image)
        
        result = {
            "success": True,
            "message": f"图片裁剪成功: ({left}, {top}, {right}, {bottom})",
            "data": {
                "image_data": result_data,
                "original_size": (image_width, image_height),
                "crop_box": (left, top, right, bottom),
                "cropped_size": cropped_image.size
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
            "error": f"图片裁剪失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def rotate_image(image_data: str, angle: float, expand: bool = True, fill_color: str = "#FFFFFF") -> list[TextContent]:
    """
    旋转图片
    
    Args:
        image_data: 图片数据（base64编码）
        angle: 旋转角度（度，正值为顺时针）
        expand: 是否扩展画布
        fill_color: 填充颜色
        
    Returns:
        旋转后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        if not validate_color_hex(fill_color):
            raise ValidationError(f"无效的颜色格式: {fill_color}")
        
        # 加载图片
        image = processor.load_image(image_data)
        original_size = image.size
        
        # 转换颜色格式
        fill_rgb = tuple(int(fill_color[i:i+2], 16) for i in (1, 3, 5))
        
        # 旋转图片
        rotated_image = image.rotate(
            -angle,  # PIL中负值为顺时针
            expand=expand,
            fillcolor=fill_rgb
        )
        
        # 转换为base64
        result_data = processor.image_to_base64(rotated_image)
        
        result = {
            "success": True,
            "message": f"图片旋转成功: {angle}度",
            "data": {
                "image_data": result_data,
                "original_size": original_size,
                "rotated_size": rotated_image.size,
                "angle": angle,
                "expand": expand,
                "fill_color": fill_color
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
            "error": f"图片旋转失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def flip_image(image_data: str, direction: str) -> list[TextContent]:
    """
    翻转图片
    
    Args:
        image_data: 图片数据（base64编码）
        direction: 翻转方向（horizontal, vertical）
        
    Returns:
        翻转后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        if direction not in ['horizontal', 'vertical']:
            raise ValidationError(f"无效的翻转方向: {direction}")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 翻转图片
        if direction == 'horizontal':
            flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
            direction_desc = "水平翻转"
        else:  # vertical
            flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
            direction_desc = "垂直翻转"
        
        # 转换为base64
        result_data = processor.image_to_base64(flipped_image)
        
        result = {
            "success": True,
            "message": f"图片{direction_desc}成功",
            "data": {
                "image_data": result_data,
                "direction": direction,
                "size": image.size
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
            "error": f"图片翻转失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]