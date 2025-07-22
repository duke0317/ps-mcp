"""
图片处理工具模块

提供图片处理的通用工具函数，包括验证、转换等功能。
"""

import base64
import io
from PIL import Image
from typing import Union, Tuple, Optional

def validate_image_source(source: str) -> bool:
    """
    验证图片源是否有效
    
    Args:
        source: 图片源（文件路径或base64编码）
        
    Returns:
        是否有效
    """
    if not source:
        return False
    
    # 检查是否为base64编码
    if source.startswith('data:image/'):
        return True
    
    # 检查是否为文件路径
    try:
        import os
        return os.path.exists(source)
    except:
        return False

def ensure_valid_image_source(source: str) -> None:
    """
    确保图片源有效，无效时抛出异常
    
    Args:
        source: 图片源
        
    Raises:
        ValueError: 图片源无效时
    """
    if not validate_image_source(source):
        raise ValueError("无效的图片源")

def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    将PIL图片转换为base64编码
    
    Args:
        image: PIL图片对象
        format: 输出格式
        
    Returns:
        base64编码的图片数据
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/{format.lower()};base64,{image_data}"

def base64_to_image(base64_data: str) -> Image.Image:
    """
    将base64编码转换为PIL图片
    
    Args:
        base64_data: base64编码的图片数据
        
    Returns:
        PIL图片对象
    """
    if base64_data.startswith('data:image/'):
        base64_data = base64_data.split(',')[1]
    
    image_data = base64.b64decode(base64_data)
    return Image.open(io.BytesIO(image_data))

def get_image_dimensions(image: Image.Image) -> Tuple[int, int]:
    """
    获取图片尺寸
    
    Args:
        image: PIL图片对象
        
    Returns:
        (宽度, 高度)
    """
    return image.size

def calculate_aspect_ratio(width: int, height: int) -> float:
    """
    计算宽高比
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        宽高比
    """
    return width / height if height != 0 else 1.0

def resize_with_aspect_ratio(original_size: Tuple[int, int], 
                           target_width: Optional[int] = None,
                           target_height: Optional[int] = None) -> Tuple[int, int]:
    """
    保持宽高比计算新尺寸
    
    Args:
        original_size: 原始尺寸 (宽, 高)
        target_width: 目标宽度
        target_height: 目标高度
        
    Returns:
        新尺寸 (宽, 高)
    """
    orig_width, orig_height = original_size
    aspect_ratio = calculate_aspect_ratio(orig_width, orig_height)
    
    if target_width and target_height:
        # 两个都指定，选择较小的缩放比例
        scale_w = target_width / orig_width
        scale_h = target_height / orig_height
        scale = min(scale_w, scale_h)
        return int(orig_width * scale), int(orig_height * scale)
    elif target_width:
        # 只指定宽度
        return target_width, int(target_width / aspect_ratio)
    elif target_height:
        # 只指定高度
        return int(target_height * aspect_ratio), target_height
    else:
        # 都不指定，返回原尺寸
        return original_size