"""
核心图片处理类
提供图片加载、保存、格式转换等基础功能
"""

from PIL import Image
import base64
import io
import os
from typing import Union, Tuple, Optional

class ImageProcessor:
    """核心图片处理类"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP']
        self.max_image_size = (4096, 4096)  # 最大图片尺寸限制
    
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