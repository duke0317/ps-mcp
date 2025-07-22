"""
测试各种图片处理功能的正确性和性能。
"""

import unittest
import asyncio
import base64
import json
from io import BytesIO
from PIL import Image

# 导入要测试的模块
from utils.image_processor import ImageProcessor
from tools.basic_ops import load_image, save_image, get_image_info, convert_format
from tools.transform import resize_image, crop_image, rotate_image, flip_image
from tools.color_adjust import adjust_brightness, adjust_contrast, adjust_saturation
from tools.filters import apply_blur, apply_sharpen, apply_sepia

class TestImageProcessor(unittest.TestCase):
    """测试ImageProcessor核心类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = ImageProcessor()
        
        # 创建测试图片
        self.test_image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        self.test_image.save(buffer, format='PNG')
        self.test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def test_load_image_from_base64(self):
        """测试从base64加载图片"""
        image = self.processor.load_image(self.test_image_data)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (100, 100))
    
    def test_image_to_base64(self):
        """测试图片转base64"""
        result = self.processor.image_to_base64(self.test_image)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    def test_get_image_info(self):
        """测试获取图片信息"""
        info = self.processor.get_image_info(self.test_image)
        self.assertEqual(info['width'], 100)
        self.assertEqual(info['height'], 100)
        self.assertEqual(info['mode'], 'RGB')

class TestBasicOperations(unittest.TestCase):
    """测试基础操作"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试图片
        self.test_image = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        self.test_image.save(buffer, format='PNG')
        self.test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def test_load_image(self):
        """测试加载图片工具"""
        result = await load_image(self.test_image_data)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertIn('data', response)
    
    async def test_get_image_info(self):
        """测试获取图片信息工具"""
        result = await get_image_info(self.test_image_data)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['width'], 100)
        self.assertEqual(response['data']['height'], 100)

class TestTransformOperations(unittest.TestCase):
    """测试几何变换操作"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试图片
        self.test_image = Image.new('RGB', (100, 100), color='green')
        buffer = BytesIO()
        self.test_image.save(buffer, format='PNG')
        self.test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def test_resize_image(self):
        """测试调整图片大小"""
        result = await resize_image(self.test_image_data, 50, 50, keep_aspect_ratio=False)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['new_size'], [50, 50])
    
    async def test_crop_image(self):
        """测试裁剪图片"""
        result = await crop_image(self.test_image_data, 10, 10, 60, 60)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['cropped_size'], [50, 50])
    
    async def test_rotate_image(self):
        """测试旋转图片"""
        result = await rotate_image(self.test_image_data, 90.0)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['angle'], 90.0)
    
    async def test_flip_image(self):
        """测试翻转图片"""
        result = await flip_image(self.test_image_data, 'horizontal')
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['direction'], 'horizontal')

class TestColorAdjustments(unittest.TestCase):
    """测试色彩调整操作"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试图片
        self.test_image = Image.new('RGB', (100, 100), color='yellow')
        buffer = BytesIO()
        self.test_image.save(buffer, format='PNG')
        self.test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def test_adjust_brightness(self):
        """测试调整亮度"""
        result = await adjust_brightness(self.test_image_data, 1.5)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['brightness_factor'], 1.5)
    
    async def test_adjust_contrast(self):
        """测试调整对比度"""
        result = await adjust_contrast(self.test_image_data, 1.2)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['contrast_factor'], 1.2)
    
    async def test_adjust_saturation(self):
        """测试调整饱和度"""
        result = await adjust_saturation(self.test_image_data, 0.8)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['saturation_factor'], 0.8)

class TestFilterEffects(unittest.TestCase):
    """测试滤镜效果操作"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试图片
        self.test_image = Image.new('RGB', (100, 100), color='purple')
        buffer = BytesIO()
        self.test_image.save(buffer, format='PNG')
        self.test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def test_apply_blur(self):
        """测试模糊滤镜"""
        result = await apply_blur(self.test_image_data, 2.0)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['radius'], 2.0)
    
    async def test_apply_sharpen(self):
        """测试锐化滤镜"""
        result = await apply_sharpen(self.test_image_data)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['filter_type'], 'sharpen')
    
    async def test_apply_sepia(self):
        """测试复古滤镜"""
        result = await apply_sepia(self.test_image_data)
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['filter_type'], 'sepia')

class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    async def test_invalid_image_data(self):
        """测试无效图片数据"""
        result = await load_image("invalid_base64_data")
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertFalse(response['success'])
        self.assertIn('error', response)
    
    async def test_invalid_parameters(self):
        """测试无效参数"""
        # 创建有效的测试图片
        test_image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        test_image.save(buffer, format='PNG')
        test_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 测试无效的亮度因子
        result = await adjust_brightness(test_image_data, 5.0)  # 超出范围
        self.assertEqual(len(result), 1)
        
        response = json.loads(result[0].text)
        self.assertFalse(response['success'])
        self.assertIn('参数验证失败', response['error'])

def run_async_test(test_func):
    """运行异步测试的辅助函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_func())
    finally:
        loop.close()

# 为异步测试方法添加同步包装器
def add_async_test_methods():
    """为异步测试方法添加同步包装器"""
    test_classes = [TestBasicOperations, TestTransformOperations, 
                   TestColorAdjustments, TestFilterEffects, TestErrorHandling]
    
    for test_class in test_classes:
        for attr_name in dir(test_class):
            attr = getattr(test_class, attr_name)
            if attr_name.startswith('test_') and asyncio.iscoroutinefunction(attr):
                # 创建同步包装器
                def make_sync_test(async_method):
                    def sync_test(self):
                        return run_async_test(lambda: async_method(self))
                    return sync_test
                
                # 替换异步方法为同步包装器
                setattr(test_class, attr_name, make_sync_test(attr))

# 添加同步包装器
add_async_test_methods()

if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)