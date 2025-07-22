"""
基础功能测试模块

测试图片处理的基础操作功能。
"""

import unittest
import asyncio
import base64
import json
from io import BytesIO
from PIL import Image

# 导入要测试的模块
from utils.image_processor import ImageProcessor
from tools.basic import load_image, save_image, get_image_info, convert_format

class TestBasicOperations(unittest.TestCase):
    """测试基础操作"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试图片
        self.test_image = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        self.test_image.save(buffer, format='PNG')
        self.test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        self.test_image_base64 = f"data:image/png;base64,{self.test_image_data}"
    
    def test_image_processor_init(self):
        """测试ImageProcessor初始化"""
        processor = ImageProcessor()
        self.assertIsNotNone(processor)
        self.assertEqual(len(processor.supported_formats), 5)
    
    def test_image_loading(self):
        """测试图片加载"""
        processor = ImageProcessor()
        image = processor.load_image(self.test_image_base64)
        self.assertIsNotNone(image)
        self.assertEqual(image.size, (100, 100))
    
    def test_image_saving(self):
        """测试图片保存"""
        processor = ImageProcessor()
        base64_data = processor.image_to_base64(self.test_image)
        self.assertTrue(base64_data.startswith('data:image/'))
    
    def test_format_conversion(self):
        """测试格式转换"""
        processor = ImageProcessor()
        # 测试PNG到JPEG转换
        jpeg_data = processor.image_to_base64(self.test_image, format='JPEG')
        self.assertTrue(jpeg_data.startswith('data:image/jpeg'))
    
    def test_image_info_extraction(self):
        """测试图片信息提取"""
        processor = ImageProcessor()
        info = processor.get_image_info(self.test_image)
        self.assertEqual(info['width'], 100)
        self.assertEqual(info['height'], 100)
        self.assertEqual(info['mode'], 'RGB')

class TestImageUtils(unittest.TestCase):
    """测试图片工具函数"""
    
    def test_aspect_ratio_calculation(self):
        """测试宽高比计算"""
        from utils.image_utils import calculate_aspect_ratio
        ratio = calculate_aspect_ratio(100, 50)
        self.assertEqual(ratio, 2.0)
    
    def test_resize_with_aspect_ratio(self):
        """测试保持宽高比的尺寸计算"""
        from utils.image_utils import resize_with_aspect_ratio
        new_size = resize_with_aspect_ratio((100, 50), target_width=200)
        self.assertEqual(new_size, (200, 100))
    
    def test_image_validation(self):
        """测试图片源验证"""
        from utils.image_utils import validate_image_source
        # 测试base64格式
        self.assertTrue(validate_image_source("data:image/png;base64,test"))
        # 测试空字符串
        self.assertFalse(validate_image_source(""))

if __name__ == '__main__':
    unittest.main()