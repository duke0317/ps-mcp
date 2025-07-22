"""
参数验证工具
提供各种参数验证功能
"""

import re
import os
import base64
from typing import Union, Tuple, Any

def validate_image_source(source: str) -> bool:
    """
    验证图片源是否有效
    
    Args:
        source: 图片源（文件路径或base64编码）
        
    Returns:
        bool: 是否有效
    """
    if not source or not isinstance(source, str):
        return False
    
    # 检查是否为文件路径
    if not source.startswith('data:image'):
        return os.path.exists(source) and os.path.isfile(source)
    
    # 检查是否为有效的base64格式
    try:
        if ',' in source:
            header, data = source.split(',', 1)
            if not header.startswith('data:image'):
                return False
            base64.b64decode(data)
            return True
    except Exception:
        return False
    
    return False

def validate_numeric_range(value: Union[int, float], min_val: Union[int, float], 
                          max_val: Union[int, float], param_name: str = None) -> bool:
    """
    验证数值是否在指定范围内
    
    Args:
        value: 要验证的值
        min_val: 最小值
        max_val: 最大值
        param_name: 参数名称（用于错误消息）
        
    Returns:
        bool: 是否在范围内
    """
    try:
        num_value = float(value)
        return min_val <= num_value <= max_val
    except (ValueError, TypeError):
        return False

def validate_color_hex(color: str) -> bool:
    """
    验证十六进制颜色格式
    
    Args:
        color: 颜色字符串
        
    Returns:
        bool: 是否为有效的十六进制颜色
    """
    if not isinstance(color, str):
        return False
    
    # 支持 #RGB, #RRGGBB, #RRGGBBAA 格式
    pattern = r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$'
    return bool(re.match(pattern, color))

def validate_image_dimensions(width: int, height: int, max_size: Tuple[int, int] = (4096, 4096)) -> bool:
    """
    验证图片尺寸是否合理
    
    Args:
        width: 宽度
        height: 高度
        max_size: 最大尺寸限制
        
    Returns:
        bool: 是否合理
    """
    try:
        w, h = int(width), int(height)
        return 1 <= w <= max_size[0] and 1 <= h <= max_size[1]
    except (ValueError, TypeError):
        return False

def validate_crop_coordinates(left: int, top: int, right: int, bottom: int, 
                            image_width: int, image_height: int) -> bool:
    """
    验证裁剪坐标是否有效
    
    Args:
        left, top, right, bottom: 裁剪坐标
        image_width, image_height: 图片尺寸
        
    Returns:
        bool: 坐标是否有效
    """
    try:
        l, t, r, b = int(left), int(top), int(right), int(bottom)
        return (0 <= l < r <= image_width and 
                0 <= t < b <= image_height)
    except (ValueError, TypeError):
        return False

def validate_resample_method(method: str) -> bool:
    """
    验证重采样方法是否支持
    
    Args:
        method: 重采样方法名称
        
    Returns:
        bool: 是否支持
    """
    valid_methods = ['NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS']
    return method.upper() in valid_methods

def validate_image_format(format_name: str) -> bool:
    """
    验证图片格式是否支持
    
    Args:
        format_name: 格式名称
        
    Returns:
        bool: 是否支持
    """
    valid_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP']
    return format_name.upper() in valid_formats

class ValidationError(Exception):
    """参数验证错误"""
    pass

def ensure_valid_image_source(source: str) -> str:
    """
    确保图片源有效，无效时抛出异常
    
    Args:
        source: 图片源
        
    Returns:
        str: 验证后的图片源
        
    Raises:
        ValidationError: 当图片源无效时
    """
    if not validate_image_source(source):
        raise ValidationError(f"无效的图片源: {source}")
    return source

def ensure_valid_dimensions(width: int, height: int) -> Tuple[int, int]:
    """
    确保图片尺寸有效，无效时抛出异常
    
    Args:
        width, height: 图片尺寸
        
    Returns:
        Tuple[int, int]: 验证后的尺寸
        
    Raises:
        ValidationError: 当尺寸无效时
    """
    if not validate_image_dimensions(width, height):
        raise ValidationError(f"无效的图片尺寸: {width}x{height}")
    return int(width), int(height)