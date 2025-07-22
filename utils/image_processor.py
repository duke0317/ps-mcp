"""
核心图片处理类
提供图片加载、保存、格式转换等基础功能
"""

from PIL import Image
import base64
import io
import os
import uuid
from typing import Union, Tuple, Optional
from config import OUTPUT_MODE, TEMP_DIR, USE_OPERATION_PREFIX

class ImageProcessor:
    """核心图片处理类"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP']
        self.max_image_size = (4096, 4096)  # 最大图片尺寸限制
        
        # 确保临时目录存在
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR, exist_ok=True)
    
    def load_image(self, source: Union[str, bytes]) -> Image.Image:
        """
        加载图片，支持文件路径、base64编码
        
        Args:
            source: 图片源，可以是文件路径或base64编码字符串
            
        Returns:
            PIL Image对象
            
        Raises:
            ValueError: 当图片源无效时
            IOError: 当图片无法加载时
        """
        try:
            if isinstance(source, str):
                if source.startswith('data:image'):
                    # base64编码的图片
                    header, data = source.split(',', 1)
                    image_data = base64.b64decode(data)
                    image = Image.open(io.BytesIO(image_data))
                else:
                    # 文件路径
                    if not os.path.exists(source):
                        raise ValueError(f"图片文件不存在: {source}")
                    image = Image.open(source)
            elif isinstance(source, bytes):
                image = Image.open(io.BytesIO(source))
            else:
                raise ValueError("不支持的图片源类型")
            
            # 检查图片尺寸
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                raise ValueError(f"图片尺寸过大，最大支持: {self.max_image_size}")
            
            return image
            
        except Exception as e:
            raise IOError(f"图片加载失败: {str(e)}")
    
    def save_image(self, image: Image.Image, output_path: str, 
                   format: str = 'PNG', quality: int = 95) -> str:
        """
        保存图片到指定路径
        
        Args:
            image: PIL Image对象
            output_path: 输出文件路径
            format: 图片格式
            quality: 图片质量 (1-100)
            
        Returns:
            保存的文件路径
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存图片
            if format.upper() == 'JPEG':
                # JPEG不支持透明度，需要转换
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                image.save(output_path, format=format, quality=quality)
            else:
                image.save(output_path, format=format)
            
            return output_path
            
        except Exception as e:
            raise IOError(f"图片保存失败: {str(e)}")
    
    def image_to_base64(self, image: Image.Image, format: str = 'PNG') -> str:
        """
        将图片转换为base64编码
        
        Args:
            image: PIL Image对象
            format: 输出格式
            
        Returns:
            base64编码的图片字符串
        """
        try:
            buffer = io.BytesIO()
            
            if format.upper() == 'JPEG':
                # JPEG处理透明度
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                image.save(buffer, format=format, quality=95)
            else:
                image.save(buffer, format=format)
            
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/{format.lower()};base64,{img_str}"
            
        except Exception as e:
            raise IOError(f"图片转换为base64失败: {str(e)}")
    
    def get_image_info(self, image: Image.Image) -> dict:
        """
        获取图片信息
        
        Args:
            image: PIL Image对象
            
        Returns:
            包含图片信息的字典
        """
        return {
            'size': image.size,
            'mode': image.mode,
            'format': image.format,
            'width': image.width,
            'height': image.height
        }
    
    def save_temp_image(self, image: Image.Image, operation: str = "processed", 
                       format: str = 'PNG', quality: int = 95) -> str:
        """
        保存图片到临时目录并返回文件路径
        
        Args:
            image: PIL Image对象
            operation: 操作名称，用于文件名前缀
            format: 图片格式
            quality: 图片质量
            
        Returns:
            临时文件路径
        """
        try:
            # 生成唯一文件名
            unique_id = str(uuid.uuid4())[:8]
            
            if USE_OPERATION_PREFIX:
                filename = f"{operation}_{unique_id}.{format.lower()}"
            else:
                filename = f"{unique_id}.{format.lower()}"
            
            temp_path = os.path.join(TEMP_DIR, filename)
            
            # 保存图片
            return self.save_image(image, temp_path, format, quality)
            
        except Exception as e:
            raise IOError(f"保存临时图片失败: {str(e)}")
    
    def output_image(self, image: Image.Image, operation: str = "processed", 
                    format: str = 'PNG', quality: int = 95) -> dict:
        """
        根据配置输出图片（文件引用模式）
        
        Args:
            image: PIL Image对象
            operation: 操作名称
            format: 图片格式
            quality: 图片质量
            
        Returns:
            包含输出信息的字典
        """
        try:
            # 保存到临时文件
            temp_path = self.save_temp_image(image, operation, format, quality)
            
            # 获取文件信息
            file_size = os.path.getsize(temp_path)
            
            return {
                "output_type": "file_reference",
                "file_path": temp_path,
                "format": format,
                "file_size": file_size,
                "operation": operation
            }
            
        except Exception as e:
            raise IOError(f"输出图片失败: {str(e)}")