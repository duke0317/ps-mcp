"""
滤镜效果工具模块

提供各种图片滤镜效果，包括模糊、锐化、边缘检测、浮雕等。
"""

from mcp.types import Tool
from utils.image_processor import ImageProcessor
from utils.validation import validate_numeric_range, ValidationError
from mcp.types import TextContent
from PIL import Image, ImageFilter, ImageOps
import json

# 全局图片处理器实例
processor = ImageProcessor()

def get_filter_tools() -> list[Tool]:
    """
    获取滤镜效果工具列表
    
    Returns:
        滤镜效果工具列表
    """
    return [
        Tool(
            name="apply_blur",
            description="应用模糊滤镜",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "radius": {
                        "type": "number",
                        "description": "模糊半径（0.1-10.0）",
                        "minimum": 0.1,
                        "maximum": 10.0
                    }
                },
                "required": ["image_data", "radius"]
            }
        ),
        Tool(
            name="apply_gaussian_blur",
            description="应用高斯模糊滤镜",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "图片数据（base64编码）"
                    },
                    "radius": {
                        "type": "number",
                        "description": "高斯模糊半径（0.1-10.0）",
                        "minimum": 0.1,
                        "maximum": 10.0
                    }
                },
                "required": ["image_data", "radius"]
            }
        ),
        Tool(
            name="apply_sharpen",
            description="应用锐化滤镜",
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
            name="apply_edge_enhance",
            description="应用边缘增强滤镜",
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
            name="apply_emboss",
            description="应用浮雕滤镜",
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
            name="apply_find_edges",
            description="应用边缘检测滤镜",
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
            name="apply_smooth",
            description="应用平滑滤镜",
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
            name="apply_contour",
            description="应用轮廓滤镜",
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
            name="apply_sepia",
            description="应用复古棕褐色滤镜",
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
            name="apply_invert",
            description="应用反色滤镜",
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
        )
    ]

async def apply_blur(image_source: str, radius: float) -> list[TextContent]:
    """
    应用模糊滤镜
    
    Args:
        image_source: 图片源（文件路径或base64编码数据）
        radius: 模糊半径
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_source:
            raise ValidationError("图片源不能为空")
        
        if not validate_numeric_range(radius, 0.1, 10.0):
            raise ValidationError(f"模糊半径必须在0.1-10.0范围内: {radius}")
        
        # 加载图片
        image = processor.load_image(image_source)
        
        # 应用模糊滤镜
        blurred_image = image.filter(ImageFilter.BoxBlur(radius))
        
        # 输出处理后的图片
        output_info = processor.output_image(blurred_image, "blur")
        
        result = {
            "success": True,
            "message": f"模糊滤镜应用成功: 半径 {radius}",
            "data": {
                **output_info,
                "filter_type": "blur",
                "radius": radius,
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
            "error": f"模糊滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_gaussian_blur(image_data: str, radius: float) -> list[TextContent]:
    """
    应用高斯模糊滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        radius: 高斯模糊半径
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        if not validate_numeric_range(radius, 0.1, 10.0):
            raise ValidationError(f"高斯模糊半径必须在0.1-10.0范围内: {radius}")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用高斯模糊滤镜
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius))
        
        # 输出处理后的图片
        output_info = processor.output_image(blurred_image, "gaussian_blur")
        
        result = {
            "success": True,
            "message": f"高斯模糊滤镜应用成功: 半径 {radius}",
            "data": {
                **output_info,
                "filter_type": "gaussian_blur",
                "radius": radius,
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
            "error": f"高斯模糊滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_sharpen(image_data: str) -> list[TextContent]:
    """
    应用锐化滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用锐化滤镜
        sharpened_image = image.filter(ImageFilter.SHARPEN)
        
        # 输出处理后的图片
        output_info = processor.output_image(sharpened_image, "sharpen")
        
        result = {
            "success": True,
            "message": "锐化滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "sharpen",
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
            "error": f"锐化滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_edge_enhance(image_data: str) -> list[TextContent]:
    """
    应用边缘增强滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用边缘增强滤镜
        enhanced_image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        # 输出处理后的图片
        output_info = processor.output_image(enhanced_image, "edge_enhance")
        
        result = {
            "success": True,
            "message": "边缘增强滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "edge_enhance",
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
            "error": f"边缘增强滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_emboss(image_data: str) -> list[TextContent]:
    """
    应用浮雕滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用浮雕滤镜
        embossed_image = image.filter(ImageFilter.EMBOSS)
        
        # 输出处理后的图片
        output_info = processor.output_image(embossed_image, "emboss")
        
        result = {
            "success": True,
            "message": "浮雕滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "emboss",
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
            "error": f"浮雕滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_find_edges(image_data: str) -> list[TextContent]:
    """
    应用边缘检测滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用边缘检测滤镜
        edges_image = image.filter(ImageFilter.FIND_EDGES)
        
        # 输出处理后的图片
        output_info = processor.output_image(edges_image, "find_edges")
        
        result = {
            "success": True,
            "message": "边缘检测滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "find_edges",
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
            "error": f"边缘检测滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_smooth(image_data: str) -> list[TextContent]:
    """
    应用平滑滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用平滑滤镜
        smooth_image = image.filter(ImageFilter.SMOOTH)
        
        # 输出处理后的图片
        output_info = processor.output_image(smooth_image, "smooth")
        
        result = {
            "success": True,
            "message": "平滑滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "smooth",
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
            "error": f"平滑滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_contour(image_data: str) -> list[TextContent]:
    """
    应用轮廓滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用轮廓滤镜
        contour_image = image.filter(ImageFilter.CONTOUR)
        
        # 输出处理后的图片
        output_info = processor.output_image(contour_image, "contour")
        
        result = {
            "success": True,
            "message": "轮廓滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "contour",
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
            "error": f"轮廓滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_sepia(image_data: str) -> list[TextContent]:
    """
    应用复古棕褐色滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 转换为RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 应用棕褐色滤镜
        pixels = image.load()
        width, height = image.size
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # 棕褐色变换公式
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                # 确保值在0-255范围内
                tr = min(255, tr)
                tg = min(255, tg)
                tb = min(255, tb)
                
                pixels[x, y] = (tr, tg, tb)
        
        # 输出处理后的图片
        output_info = processor.output_image(image, "sepia")
        
        result = {
            "success": True,
            "message": "复古棕褐色滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "sepia",
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
            "error": f"复古棕褐色滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

async def apply_invert(image_data: str) -> list[TextContent]:
    """
    应用反色滤镜
    
    Args:
        image_data: 图片数据（base64编码）
        
    Returns:
        应用滤镜后的图片数据
    """
    try:
        # 验证参数
        if not image_data:
            raise ValidationError("图片数据不能为空")
        
        # 加载图片
        image = processor.load_image(image_data)
        
        # 应用反色滤镜
        inverted_image = ImageOps.invert(image.convert('RGB'))
        
        # 输出处理后的图片
        output_info = processor.output_image(inverted_image, "invert")
        
        result = {
            "success": True,
            "message": "反色滤镜应用成功",
            "data": {
                **output_info,
                "filter_type": "invert",
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
            "error": f"反色滤镜应用失败: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]