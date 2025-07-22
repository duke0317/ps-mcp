"""
性能优化工具模块

提供图片处理的性能优化功能，包括缓存、内存管理、并发控制等。
"""

import time
import hashlib
import os
import gc
import psutil
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from PIL import Image
import json

from config import (
    MAX_CONCURRENT_TASKS, ENABLE_CACHE,
    CACHE_SIZE_MB, PROCESSING_TIMEOUT
)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "total_operations": 0,
            "total_processing_time": 0.0,
            "memory_usage": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        self.start_time = time.time()
    
    def record_operation(self, operation_name: str, processing_time: float, 
                        memory_used: float, cache_hit: bool = False, error: bool = False):
        """记录操作指标"""
        self.metrics["total_operations"] += 1
        self.metrics["total_processing_time"] += processing_time
        self.metrics["memory_usage"].append(memory_used)
        
        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
            
        if error:
            self.metrics["errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        uptime = time.time() - self.start_time
        avg_processing_time = (self.metrics["total_processing_time"] / 
                             max(self.metrics["total_operations"], 1))
        avg_memory = (sum(self.metrics["memory_usage"]) / 
                     max(len(self.metrics["memory_usage"]), 1))
        cache_hit_rate = (self.metrics["cache_hits"] / 
                         max(self.metrics["cache_hits"] + self.metrics["cache_misses"], 1))
        
        return {
            "uptime_seconds": uptime,
            "total_operations": self.metrics["total_operations"],
            "average_processing_time": avg_processing_time,
            "average_memory_usage_mb": avg_memory,
            "cache_hit_rate": cache_hit_rate,
            "error_rate": self.metrics["errors"] / max(self.metrics["total_operations"], 1),
            "operations_per_second": self.metrics["total_operations"] / max(uptime, 1)
        }

class ImageCache:
    """图片缓存管理器"""
    
    def __init__(self, max_size_mb: int = CACHE_SIZE_MB):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache = {}
        self.access_times = {}
        self.current_size = 0
        self.enabled = ENABLE_CACHE
    
    def _get_cache_key(self, image_source: str, operation: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 创建参数的哈希值
        params_str = json.dumps(params, sort_keys=True)
        combined = f"{image_source}:{operation}:{params_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _estimate_image_size(self, image: Image.Image) -> int:
        """估算图片内存大小"""
        # 估算：宽度 × 高度 × 通道数 × 字节数
        channels = len(image.getbands())
        return image.width * image.height * channels
    
    def _cleanup_cache(self, required_space: int):
        """清理缓存以释放空间"""
        if not self.enabled:
            return
            
        # 按访问时间排序，删除最久未使用的项
        sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
        
        for cache_key, _ in sorted_items:
            if self.current_size + required_space <= self.max_size_bytes:
                break
                
            if cache_key in self.cache:
                item_size = self.cache[cache_key]["size"]
                del self.cache[cache_key]
                del self.access_times[cache_key]
                self.current_size -= item_size
    
    def get(self, image_source: str, operation: str, params: Dict[str, Any]) -> Optional[str]:
        """从缓存获取结果"""
        if not self.enabled:
            return None
            
        cache_key = self._get_cache_key(image_source, operation, params)
        
        if cache_key in self.cache:
            self.access_times[cache_key] = time.time()
            return self.cache[cache_key]["result"]
        
        return None
    
    def put(self, image_source: str, operation: str, params: Dict[str, Any], 
            result: str, result_image: Optional[Image.Image] = None):
        """将结果存入缓存"""
        if not self.enabled:
            return
            
        cache_key = self._get_cache_key(image_source, operation, params)
        
        # 估算结果大小
        if result_image:
            item_size = self._estimate_image_size(result_image)
        else:
            # 估算base64字符串大小
            item_size = len(result.encode()) if isinstance(result, str) else 1024
        
        # 检查是否需要清理缓存
        if self.current_size + item_size > self.max_size_bytes:
            self._cleanup_cache(item_size)
        
        # 存储到缓存
        self.cache[cache_key] = {
            "result": result,
            "size": item_size,
            "timestamp": time.time()
        }
        self.access_times[cache_key] = time.time()
        self.current_size += item_size
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
        self.current_size = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "enabled": self.enabled,
            "items_count": len(self.cache),
            "current_size_mb": self.current_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "usage_percentage": (self.current_size / self.max_size_bytes) * 100
        }

class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self.active_tasks = 0
        self.max_tasks = MAX_CONCURRENT_TASKS
        self.task_semaphore = asyncio.Semaphore(self.max_tasks)
    
    async def acquire_task_slot(self):
        """获取任务槽位"""
        await self.task_semaphore.acquire()
        self.active_tasks += 1
    
    def release_task_slot(self):
        """释放任务槽位"""
        if self.active_tasks > 0:
            self.active_tasks -= 1
            self.task_semaphore.release()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),  # 物理内存
            "vms_mb": memory_info.vms / (1024 * 1024),  # 虚拟内存
            "percent": process.memory_percent()
        }
    
    def cleanup_memory(self):
        """清理内存"""
        gc.collect()  # 强制垃圾回收
    
    def get_stats(self) -> Dict[str, Any]:
        """获取资源统计"""
        memory = self.get_memory_usage()
        
        return {
            "active_tasks": self.active_tasks,
            "max_tasks": self.max_tasks,
            "memory_usage": memory,
            "available_slots": self.max_tasks - self.active_tasks
        }

# 全局实例
performance_monitor = PerformanceMonitor()
image_cache = ImageCache()
resource_manager = ResourceManager()

def performance_tracking(operation_name: str):
    """性能跟踪装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = resource_manager.get_memory_usage()["rss_mb"]
            cache_hit = False
            error = False
            
            try:
                # 检查缓存
                if len(args) > 0 and isinstance(args[0], dict):
                    arguments = args[0]
                    image_source = arguments.get("image_source")
                    if image_source:
                        cached_result = image_cache.get(image_source, operation_name, arguments)
                        if cached_result:
                            cache_hit = True
                            return [{"type": "text", "text": cached_result}]
                
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                if not cache_hit and len(args) > 0 and isinstance(args[0], dict):
                    arguments = args[0]
                    image_source = arguments.get("image_source")
                    if image_source and result and len(result) > 0:
                        result_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
                        image_cache.put(image_source, operation_name, arguments, result_text)
                
                return result
                
            except Exception as e:
                error = True
                raise
            finally:
                end_time = time.time()
                end_memory = resource_manager.get_memory_usage()["rss_mb"]
                processing_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                performance_monitor.record_operation(
                    operation_name, processing_time, memory_used, cache_hit, error
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = resource_manager.get_memory_usage()["rss_mb"]
            error = False
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise
            finally:
                end_time = time.time()
                end_memory = resource_manager.get_memory_usage()["rss_mb"]
                processing_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                performance_monitor.record_operation(
                    operation_name, processing_time, memory_used, False, error
                )
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

async def process_with_timeout(coro, timeout: float = PROCESSING_TIMEOUT):
    """带超时的异步处理"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"操作超时（{timeout}秒）")

class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, max_workers: int = MAX_CONCURRENT_TASKS):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, tasks: List[Callable], progress_callback: Optional[Callable] = None):
        """批量处理任务"""
        results = []
        completed = 0
        total = len(tasks)
        
        # 提交所有任务
        future_to_index = {}
        for i, task in enumerate(tasks):
            future = self.executor.submit(task)
            future_to_index[future] = i
        
        # 收集结果
        for future in as_completed(future_to_index.keys()):
            index = future_to_index[future]
            try:
                result = future.result()
                results.append((index, result, None))
            except Exception as e:
                results.append((index, None, str(e)))
            
            completed += 1
            if progress_callback:
                await progress_callback(completed, total)
        
        # 按原始顺序排序结果
        results.sort(key=lambda x: x[0])
        return results
    
    def shutdown(self):
        """关闭处理器"""
        self.executor.shutdown(wait=True)

def optimize_image_for_processing(image: Image.Image, max_dimension: int = 2048) -> Image.Image:
    """优化图片以提高处理性能"""
    # 如果图片太大，先缩小
    if max(image.width, image.height) > max_dimension:
        ratio = max_dimension / max(image.width, image.height)
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image

def get_performance_stats() -> Dict[str, Any]:
    """获取完整的性能统计"""
    return {
        "monitor": performance_monitor.get_stats(),
        "cache": image_cache.get_stats(),
        "resources": resource_manager.get_stats(),
        "timestamp": time.time()
    }

def reset_performance_stats():
    """重置性能统计"""
    global performance_monitor, image_cache
    performance_monitor = PerformanceMonitor()
    image_cache.clear()
    resource_manager.cleanup_memory()

# 导出的工具函数
__all__ = [
    "PerformanceMonitor",
    "ImageCache", 
    "ResourceManager",
    "BatchProcessor",
    "performance_tracking",
    "process_with_timeout",
    "optimize_image_for_processing",
    "get_performance_stats",
    "reset_performance_stats",
    "performance_monitor",
    "image_cache",
    "resource_manager"
]