"""
色彩调整工具模块

提供图片的色彩调整功能，包括亮度、对比度、饱和度、色调等调整。
"""

from mcp.types import Tool
from utils.image_processor import ImageProcessor
from utils.validation import validate_numeric_range, ValidationError
from mcp.types import TextContent
from PIL import Image, ImageEnhance, ImageFilter
import json

# 全局图片处理器实例
processor = ImageProcessor()

def get_color_adjust_tools() -> list[Tool]:
    """
    获取色彩调整工具列表
    
    Returns:
        色彩调整工具列表
    """
    return [
        Tool(
            name="adjust_brightness",
            description="调整图片亮度",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    },
                    "factor": {
                        "type": "number",
                        "description": "亮度调整因子（0.0-2.0，1.0为原始亮度）",
                        "minimum": 0.0,
                        "maximum": 2.0
                    }
                },
                "required": ["image_source", "factor"]
            }
        ),
        Tool(
            name="adjust_contrast",
            description="调整图片对比度",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    },
                    "factor": {
                        "type": "number",
                        "description": "对比度调整因子（0.0-2.0，1.0为原始对比度）",
                        "minimum": 0.0,
                        "maximum": 2.0
                    }
                },
                "required": ["image_source", "factor"]
            }
        ),
        Tool(
            name="adjust_saturation",
            description="调整图片饱和度",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    },
                    "factor": {
                        "type": "number",
                        "description": "饱和度调整因子（0.0-2.0，1.0为原始饱和度，0.0为灰度）",
                        "minimum": 0.0,
                        "maximum": 2.0
                    }
                },
                "required": ["image_source", "factor"]
            }
        ),
        Tool(
            name="adjust_sharpness",
            description="调整图片锐度",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    },
                    "factor": {
                        "type": "number",
                        "description": "锐度调整因子（0.0-2.0，1.0为原始锐度）",
                        "minimum": 0.0,
                        "maximum": 2.0
                    }
                },
                "required": ["image_source", "factor"]
            }
        ),
        Tool(
            name="convert_to_grayscale",
            description="将图片转换为灰度图",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    }
                },
                "required": ["image_source"]
            }
        ),
        Tool(
            name="adjust_gamma",
            description="调整图片伽马值",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    },
                    "gamma": {
                        "type": "number",
                        "description": "伽马值（0.1-3.0，1.0为原始值）",
                        "minimum": 0.1,
                        "maximum": 3.0
                    }
                },
                "required": ["image_source", "gamma"]
            }
        ),
        Tool(
            name="adjust_opacity",
            description="调整图片不透明度",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "图片数据（base64编码）或文件路径"
                    },
                    "opacity": {
                        "type": "number",
                        "description": "不透明度值（0.0-1.0，0.0为完全透明，1.0为完全不透明）",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["image_source", "opacity"]
            }
        )
    ]

async def adjust_brightness(image_source: str, factor: float) -> list[TextContent]:
    """
    调整图片亮度
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        factor: 亮度调整因子（0.0-2.0）
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据或路径不能为空")
        
        if not validate_numeric_range(factor, 0.0, 2.0):
            raise ValidationError(f"亮度因子必须在0.0-2.0范围内: {factor}")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 调整亮度
        enhancer = ImageEnhance.Brightness(image)
        enhanced_image = enhancer.enhance(factor)
        
        # 输出处理后的图片
        output_info = processor.output_image(enhanced_image, "brightness")
        
        result = {
            "success": True,
            "message": f"亮度调整成功: 因子 {factor}",
            "data": {
                **output_info,
                "brightness_factor": factor,
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

async def adjust_opacity(image_source: str, opacity: float) -> list[TextContent]:
    """
    调整图片不透明度
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        opacity: 不透明度值（0.0-1.0）
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据不能为空")
        
        if not validate_numeric_range(opacity, 0.0, 1.0):
            raise ValidationError(f"不透明度值必须在0.0-1.0范围内: {opacity}")
        
        # 加载图片
        image = processor.load_image(image_source)
        original_mode = image.mode
        
        # 确保图片有alpha通道
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 获取图片数据
        data = image.getdata()
        
        # 调整alpha通道
        new_data = []
        for item in data:
            # item是(R, G, B, A)元组
            r, g, b, a = item
            # 计算新的alpha值
            new_alpha = int(a * opacity)
            new_data.append((r, g, b, new_alpha))
        
        # 创建新图片
        opacity_image = Image.new('RGBA', image.size)
        opacity_image.putdata(new_data)
        
        # 输出处理后的图片
        output_info = processor.output_image(opacity_image, "opacity")
        
        result = {
            "success": True,
            "message": f"不透明度调整成功: {opacity}",
            "data": {
                **output_info,
                "opacity_value": opacity,
                "original_mode": original_mode,
                "new_mode": opacity_image.mode,
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
            "error": f"不透明度调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"亮度调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def adjust_contrast(image_source: str, factor: float) -> list[TextContent]:
    """
    调整图片对比度
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        factor: 对比度调整因子（0.0-2.0）
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据或路径不能为空")
        
        if not validate_numeric_range(factor, 0.0, 2.0):
            raise ValidationError(f"对比度因子必须在0.0-2.0范围内: {factor}")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 调整对比度
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(factor)
        
        # 输出处理后的图片
        output_info = processor.output_image(enhanced_image, "contrast")
        
        result = {
            "success": True,
            "message": f"对比度调整成功: 因子 {factor}",
            "data": {
                **output_info,
                "contrast_factor": factor,
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
            "error": f"对比度调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def adjust_saturation(image_source: str, factor: float) -> list[TextContent]:
    """
    调整图片饱和度
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        factor: 饱和度调整因子（0.0-2.0）
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据不能为空")
        
        if not validate_numeric_range(factor, 0.0, 2.0):
            raise ValidationError(f"饱和度因子必须在0.0-2.0范围内: {factor}")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 调整饱和度
        enhancer = ImageEnhance.Color(image)
        enhanced_image = enhancer.enhance(factor)
        
        # 输出处理后的图片
        output_info = processor.output_image(enhanced_image, "saturation")
        
        result = {
            "success": True,
            "message": f"饱和度调整成功: 因子 {factor}",
            "data": {
                **output_info,
                "saturation_factor": factor,
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
            "error": f"饱和度调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def adjust_sharpness(image_source: str, factor: float) -> list[TextContent]:
    """
    调整图片锐度
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        factor: 锐度调整因子（0.0-2.0）
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据不能为空")
        
        if not validate_numeric_range(factor, 0.0, 2.0):
            raise ValidationError(f"锐度因子必须在0.0-2.0范围内: {factor}")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 调整锐度
        enhancer = ImageEnhance.Sharpness(image)
        enhanced_image = enhancer.enhance(factor)
        
        # 输出处理后的图片
        output_info = processor.output_image(enhanced_image, "sharpness")
        
        result = {
            "success": True,
            "message": f"锐度调整成功: 因子 {factor}",
            "data": {
                **output_info,
                "sharpness_factor": factor,
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
            "error": f"锐度调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def convert_to_grayscale(image_source: str) -> list[TextContent]:
    """
    将图片转换为灰度图
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        
    Returns:
        灰度图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 转换为灰度图
        grayscale_image = image.convert('L')
        
        # 输出处理后的图片
        output_info = processor.output_image(grayscale_image, "grayscale")
        
        result = {
            "success": True,
            "message": "图片转换为灰度图成功",
            "data": {
                **output_info,
                "original_mode": image.mode,
                "new_mode": grayscale_image.mode,
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
            "error": f"灰度转换失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def adjust_gamma(image_source: str, gamma: float) -> list[TextContent]:
    """
    调整图片伽马值
    
    Args:
        image_source: 图片数据（base64编码）或文件路径
        gamma: 伽马值（0.1-3.0）
        
    Returns:
        调整后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片数据不能为空")
        
        if not validate_numeric_range(gamma, 0.1, 3.0):
            raise ValidationError(f"伽马值必须在0.1-3.0范围内: {gamma}")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 创建伽马校正查找表
        gamma_table = [int(((i / 255.0) ** (1.0 / gamma)) * 255) for i in range(256)]
        
        # 应用伽马校正
        if image.mode == 'RGB':
            # 对RGB图片分别处理每个通道
            r, g, b = image.split()
            r = r.point(gamma_table)
            g = g.point(gamma_table)
            b = b.point(gamma_table)
            gamma_image = Image.merge('RGB', (r, g, b))
        elif image.mode == 'L':
            # 对灰度图直接处理
            gamma_image = image.point(gamma_table)
        else:
            # 其他模式先转换为RGB
            rgb_image = image.convert('RGB')
            r, g, b = rgb_image.split()
            r = r.point(gamma_table)
            g = g.point(gamma_table)
            b = b.point(gamma_table)
            gamma_image = Image.merge('RGB', (r, g, b))
        
        # 输出处理后的图片
        output_info = processor.output_image(gamma_image, "gamma")
        
        result = {
            "success": True,
            "message": f"伽马调整成功: 伽马值 {gamma}",
            "data": {
                **output_info,
                "gamma_value": gamma,
                "original_mode": image.mode,
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
            "error": f"伽马调整失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]