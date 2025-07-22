"""
高级功能测试模块

测试特效处理、高级功能和性能优化等模块的功能。
"""

import unittest
import asyncio
import json
import base64
import os
import tempfile
from PIL import Image
import io

# 导入测试目标
from tools.effects import (
    add_border, create_silhouette, add_shadow, 
    add_watermark, apply_vignette, create_polaroid
)
from tools.advanced import (
    batch_resize, create_collage, create_thumbnail_grid,
    blend_images, extract_colors, create_gif
)
from utils.performance import (
    PerformanceMonitor, ImageCache, ResourceManager,
    performance_tracking, get_performance_stats, reset_performance_stats
)

class TestEffects(unittest.TestCase):
    """测试特效处理功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建测试图片
        self.test_image = Image.new("RGB", (200, 200), "red")
        buffer = io.BytesIO()
        self.test_image.save(buffer, format="PNG")
        self.test_image_base64 = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
        
        # 创建测试水印图片
        self.watermark_image = Image.new("RGBA", (50, 50), (255, 255, 255, 128))
        buffer = io.BytesIO()
        self.watermark_image.save(buffer, format="PNG")
        self.watermark_base64 = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    
    def test_add_border(self):
        """测试添加边框"""
        async def run_test():
            arguments = {
                "image_source": self.test_image_base64,
                "border_width": 10,
                "border_color": "#000000",
                "border_style": "solid"
            }
            result = await add_border(arguments)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
            self.assertIn("result", result_data)
        
        asyncio.run(run_test())
    
    def test_create_silhouette(self):
        """测试创建剪影"""
        async def run_test():
            arguments = {
                "image_source": self.test_image_base64,
                "threshold": 128,
                "silhouette_color": "#000000",
                "background_color": "#FFFFFF"
            }
            result = await create_silhouette(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_add_shadow(self):
        """测试添加阴影"""
        async def run_test():
            arguments = {
                "image_source": self.test_image_base64,
                "offset_x": 5,
                "offset_y": 5,
                "blur_radius": 3,
                "shadow_color": "#808080",
                "shadow_opacity": 0.5
            }
            result = await add_shadow(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_add_watermark(self):
        """测试添加水印"""
        async def run_test():
            arguments = {
                "image_source": self.test_image_base64,
                "watermark_source": self.watermark_base64,
                "position": "bottom_right",
                "opacity": 0.7,
                "scale": 0.2
            }
            result = await add_watermark(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_apply_vignette(self):
        """测试添加暗角"""
        async def run_test():
            arguments = {
                "image_source": self.test_image_base64,
                "strength": 0.5,
                "radius": 0.8,
                "color": "#000000"
            }
            result = await apply_vignette(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_create_polaroid(self):
        """测试创建宝丽来效果"""
        async def run_test():
            arguments = {
                "image_source": self.test_image_base64,
                "border_width": 20,
                "bottom_border": 60,
                "border_color": "#FFFFFF",
                "rotation": 5,
                "caption": "Test Photo"
            }
            result = await create_polaroid(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())

class TestAdvanced(unittest.TestCase):
    """测试高级功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建多个测试图片
        self.test_images = []
        for i, color in enumerate(["red", "green", "blue"]):
            image = Image.new("RGB", (100, 100), color)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_base64 = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
            self.test_images.append(image_base64)
    
    def test_batch_resize(self):
        """测试批量调整大小"""
        async def run_test():
            arguments = {
                "image_sources": self.test_images,
                "width": 50,
                "height": 50,
                "maintain_aspect_ratio": True
            }
            result = await batch_resize(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
            self.assertIn("results", result_data)
            self.assertEqual(len(result_data["results"]), 3)
        
        asyncio.run(run_test())
    
    def test_create_collage(self):
        """测试创建拼贴"""
        async def run_test():
            arguments = {
                "image_sources": self.test_images,
                "layout": "grid",
                "spacing": 10,
                "background_color": "#FFFFFF"
            }
            result = await create_collage(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
            self.assertIn("result", result_data)
        
        asyncio.run(run_test())
    
    def test_create_thumbnail_grid(self):
        """测试创建缩略图网格"""
        async def run_test():
            arguments = {
                "image_sources": self.test_images,
                "thumbnail_size": 80,
                "columns": 2,
                "spacing": 5
            }
            result = await create_thumbnail_grid(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_blend_images(self):
        """测试混合图片"""
        async def run_test():
            arguments = {
                "image1_source": self.test_images[0],
                "image2_source": self.test_images[1],
                "blend_mode": "normal",
                "opacity": 0.5
            }
            result = await blend_images(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_extract_colors(self):
        """测试提取颜色"""
        async def run_test():
            arguments = {
                "image_source": self.test_images[0],
                "color_count": 3,
                "create_palette": True
            }
            result = await extract_colors(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
            self.assertIn("colors", result_data)
            self.assertIn("palette", result_data)
        
        asyncio.run(run_test())
    
    def test_create_gif(self):
        """测试创建GIF"""
        async def run_test():
            arguments = {
                "image_sources": self.test_images,
                "duration": 500,
                "loop": True,
                "optimize": True
            }
            result = await create_gif(arguments)
            self.assertIsInstance(result, list)
            
            result_data = json.loads(result[0].text)
            self.assertTrue(result_data["success"])
            self.assertIn("result", result_data)
        
        asyncio.run(run_test())

class TestPerformance(unittest.TestCase):
    """测试性能优化功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.monitor = PerformanceMonitor()
        self.cache = ImageCache(max_size_mb=1)  # 1MB缓存用于测试
        self.resource_manager = ResourceManager()
    
    def test_performance_monitor(self):
        """测试性能监控器"""
        # 记录一些操作
        self.monitor.record_operation("test_op", 0.1, 10.0, cache_hit=False, error=False)
        self.monitor.record_operation("test_op", 0.2, 15.0, cache_hit=True, error=False)
        self.monitor.record_operation("test_op", 0.15, 12.0, cache_hit=False, error=True)
        
        stats = self.monitor.get_stats()
        
        self.assertEqual(stats["total_operations"], 3)
        self.assertAlmostEqual(stats["average_processing_time"], 0.15, places=2)
        self.assertAlmostEqual(stats["average_memory_usage_mb"], 12.33, places=1)
        self.assertAlmostEqual(stats["cache_hit_rate"], 0.5, places=1)
        self.assertAlmostEqual(stats["error_rate"], 1/3, places=2)
    
    def test_image_cache(self):
        """测试图片缓存"""
        # 测试缓存存储和获取
        image_source = "test_image"
        operation = "resize"
        params = {"width": 100, "height": 100}
        result = "cached_result"
        
        # 存储到缓存
        self.cache.put(image_source, operation, params, result)
        
        # 从缓存获取
        cached_result = self.cache.get(image_source, operation, params)
        self.assertEqual(cached_result, result)
        
        # 测试缓存未命中
        different_params = {"width": 200, "height": 200}
        cached_result = self.cache.get(image_source, operation, different_params)
        self.assertIsNone(cached_result)
        
        # 测试缓存统计
        stats = self.cache.get_stats()
        self.assertEqual(stats["items_count"], 1)
        self.assertTrue(stats["enabled"])
    
    def test_resource_manager(self):
        """测试资源管理器"""
        async def run_test():
            # 测试获取和释放任务槽位
            initial_active = self.resource_manager.active_tasks
            
            await self.resource_manager.acquire_task_slot()
            self.assertEqual(self.resource_manager.active_tasks, initial_active + 1)
            
            self.resource_manager.release_task_slot()
            self.assertEqual(self.resource_manager.active_tasks, initial_active)
            
            # 测试内存使用情况
            memory_usage = self.resource_manager.get_memory_usage()
            self.assertIn("rss_mb", memory_usage)
            self.assertIn("vms_mb", memory_usage)
            self.assertIn("percent", memory_usage)
            
            # 测试统计信息
            stats = self.resource_manager.get_stats()
            self.assertIn("active_tasks", stats)
            self.assertIn("max_tasks", stats)
            self.assertIn("memory_usage", stats)
        
        asyncio.run(run_test())
    
    def test_performance_tracking_decorator(self):
        """测试性能跟踪装饰器"""
        @performance_tracking("test_operation")
        async def test_function(arguments):
            await asyncio.sleep(0.01)  # 模拟处理时间
            return [{"type": "text", "text": "success"}]
        
        async def run_test():
            arguments = {"test": "data"}
            result = await test_function(arguments)
            
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
        
        asyncio.run(run_test())
    
    def test_performance_stats(self):
        """测试性能统计功能"""
        # 获取性能统计
        stats = get_performance_stats()
        
        self.assertIn("monitor", stats)
        self.assertIn("cache", stats)
        self.assertIn("resources", stats)
        self.assertIn("timestamp", stats)
        
        # 重置性能统计
        reset_performance_stats()
        
        # 验证统计已重置
        new_stats = get_performance_stats()
        self.assertEqual(new_stats["monitor"]["total_operations"], 0)

class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    def test_invalid_image_source(self):
        """测试无效图片源"""
        async def run_test():
            arguments = {
                "image_source": "invalid_base64_data",
                "border_width": 10,
                "border_color": "#000000"
            }
            result = await add_border(arguments)
            
            result_data = json.loads(result[0].text)
            self.assertFalse(result_data["success"])
            self.assertIn("error", result_data)
        
        asyncio.run(run_test())
    
    def test_invalid_parameters(self):
        """测试无效参数"""
        # 创建有效的测试图片
        test_image = Image.new("RGB", (100, 100), "red")
        buffer = io.BytesIO()
        test_image.save(buffer, format="PNG")
        test_image_base64 = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
        
        async def run_test():
            # 测试无效的边框宽度
            arguments = {
                "image_source": test_image_base64,
                "border_width": -5,  # 无效值
                "border_color": "#000000"
            }
            result = await add_border(arguments)
            
            result_data = json.loads(result[0].text)
            self.assertFalse(result_data["success"])
        
        asyncio.run(run_test())
    
    def test_empty_batch_operation(self):
        """测试空批量操作"""
        async def run_test():
            arguments = {
                "image_sources": [],  # 空列表
                "width": 100,
                "height": 100
            }
            result = await batch_resize(arguments)
            
            result_data = json.loads(result[0].text)
            self.assertFalse(result_data["success"])
        
        asyncio.run(run_test())

def run_async_test(test_func):
    """运行异步测试的辅助函数"""
    def wrapper(self):
        asyncio.run(test_func(self))
    return wrapper

if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)