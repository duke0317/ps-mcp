#!/usr/bin/env python3
"""
使用FastMCP的PS-MCP图片处理服务器 - 主程序
集成所有tools目录下的工具方法
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import traceback
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp.server.fastmcp import FastMCP

# 导入所有工具模块的方法
# Basic tools
from tools.basic import (
    load_image as basic_load_image,
    save_image as basic_save_image,
    get_image_info as basic_get_image_info,
    convert_format as basic_convert_format
)

# Transform tools
from tools.transform import (
    resize_image as transform_resize_image,
    crop_image as transform_crop_image,
    rotate_image as transform_rotate_image,
    flip_image as transform_flip_image
)

# Filter tools
from tools.filters import (
    apply_blur as filters_apply_blur,
    apply_gaussian_blur as filters_apply_gaussian_blur,
    apply_sharpen as filters_apply_sharpen,
    apply_edge_enhance as filters_apply_edge_enhance,
    apply_emboss as filters_apply_emboss,
    apply_find_edges as filters_apply_find_edges,
    apply_smooth as filters_apply_smooth,
    apply_contour as filters_apply_contour,
    apply_sepia as filters_apply_sepia,
    apply_invert as filters_apply_invert
)

# Color adjustment tools
from tools.color_adjust import (
    adjust_brightness as color_adjust_brightness,
    adjust_contrast as color_adjust_contrast,
    adjust_saturation as color_adjust_saturation,
    adjust_sharpness as color_adjust_sharpness,
    convert_to_grayscale as color_convert_to_grayscale,
    adjust_gamma as color_adjust_gamma
)

# Effects tools
from tools.effects import (
    add_border as effects_add_border,
    create_silhouette as effects_create_silhouette,
    add_shadow  as effects_add_shadow,
    add_watermark as effects_add_watermark,
    apply_vignette as effects_apply_vignette,
    create_polaroid as effects_create_polaroid
)

# Advanced tools
from tools.advanced import (
    batch_resize as advanced_batch_resize,
    create_collage as advanced_create_collage,
    create_thumbnail_grid as advanced_create_thumbnail_grid,
    blend_images as advanced_blend_images,
    extract_colors as advanced_extract_colors,
    create_gif as advanced_create_gif
)

# Performance utilities
from utils.performance import get_performance_stats as utils_get_performance_stats, reset_performance_stats as utils_reset_performance_stats

# 辅助函数：安全地运行异步函数
def safe_run_async(coro):
    """安全地运行异步函数，处理事件循环问题"""
    try:
        # 尝试获取当前事件循环
        loop = asyncio.get_running_loop()
        # 如果已经在事件循环中，创建一个任务
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # 没有运行的事件循环，可以直接使用asyncio.run
        return asyncio.run(coro)

# 创建FastMCP服务器
mcp = FastMCP("PS-MCP")

# ============ 基础工具 ============

@mcp.tool()
def load_image(source: str) -> str:
    """加载图片文件或base64编码的图片"""
    try:
        result = safe_run_async(basic_load_image(source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"加载图片失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def save_image(image_source: str, output_path: str, format: str = "PNG", quality: int = 95) -> str:
    """保存图片到指定路径"""
    try:
        result = safe_run_async(basic_save_image(image_source, output_path, format, quality))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"保存图片失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_image_info(image_source: str) -> str:
    """获取图片基本信息"""
    try:
        result = safe_run_async(basic_get_image_info(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"获取图片信息失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def convert_format(image_source: str, target_format: str, quality: int = 95) -> str:
    """转换图片格式"""
    try:
        result = safe_run_async(basic_convert_format(image_source, target_format, quality))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"转换图片格式失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# ============ 几何变换工具 ============

@mcp.tool()
def resize_image(image_source: str, width: int, height: int, keep_aspect_ratio: bool = True, resample: str = "LANCZOS") -> str:
    """调整图片大小"""
    try:
        result = safe_run_async(transform_resize_image(image_source, width, height, keep_aspect_ratio, resample))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整图片大小失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def crop_image(image_source: str, left: int, top: int, right: int, bottom: int) -> str:
    """裁剪图片"""
    try:
        result = safe_run_async(transform_crop_image(image_source, left, top, right, bottom))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"裁剪图片失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def rotate_image(image_source: str, angle: float, expand: bool = True, fill_color: str = "#FFFFFF") -> str:
    """旋转图片"""
    try:
        result = safe_run_async(transform_rotate_image(image_source, angle, expand, fill_color))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"旋转图片失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def flip_image(image_source: str, direction: str) -> str:
    """翻转图片"""
    try:
        result = safe_run_async(transform_flip_image(image_source, direction))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"翻转图片失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# ============ 滤镜工具 ============

@mcp.tool()
def apply_blur(image_source: str, radius: float) -> str:
    """应用模糊滤镜"""
    try:
        result = safe_run_async(filters_apply_blur(image_source, radius))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用模糊效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_gaussian_blur(image_source: str, radius: float) -> str:
    """应用高斯模糊滤镜"""
    try:
        result = safe_run_async(filters_apply_gaussian_blur(image_source, radius))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用高斯模糊失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_sharpen(image_source: str) -> str:
    """应用锐化滤镜"""
    try:
        result = safe_run_async(filters_apply_sharpen(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用锐化效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_edge_enhance(image_source: str) -> str:
    """应用边缘增强滤镜"""
    try:
        result = safe_run_async(filters_apply_edge_enhance(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用边缘增强失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_emboss(image_source: str) -> str:
    """应用浮雕滤镜"""
    try:
        result = safe_run_async(filters_apply_emboss(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用浮雕效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_find_edges(image_source: str) -> str:
    """应用边缘检测滤镜"""
    try:
        result = safe_run_async(filters_apply_find_edges(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用边缘检测失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_smooth(image_source: str) -> str:
    """应用平滑滤镜"""
    try:
        result = safe_run_async(filters_apply_smooth(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用平滑效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_contour(image_source: str) -> str:
    """应用轮廓滤镜"""
    try:
        result = safe_run_async(filters_apply_contour(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用轮廓效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_sepia(image_source: str) -> str:
    """应用复古棕褐色滤镜"""
    try:
        result = safe_run_async(filters_apply_sepia(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用复古滤镜失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_invert(image_source: str) -> str:
    """应用反色滤镜"""
    try:
        result = safe_run_async(filters_apply_invert(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用反色效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# ============ 色彩调整工具 ============

@mcp.tool()
def adjust_brightness(image_source: str, factor: float) -> str:
    """调整图片亮度"""
    try:
        result = safe_run_async(color_adjust_brightness(image_source, factor))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整亮度失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def adjust_contrast(image_source: str, factor: float) -> str:
    """调整图片对比度"""
    try:
        result = safe_run_async(color_adjust_contrast(image_source, factor))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整对比度失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def adjust_saturation(image_source: str, factor: float) -> str:
    """调整图片饱和度"""
    try:
        result = safe_run_async(color_adjust_saturation(image_source, factor))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整饱和度失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def adjust_sharpness(image_source: str, factor: float) -> str:
    """调整图片锐度"""
    try:
        result = safe_run_async(color_adjust_sharpness(image_source, factor))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整锐度失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def convert_to_grayscale(image_source: str) -> str:
    """将图片转换为灰度图"""
    try:
        result = safe_run_async(color_convert_to_grayscale(image_source))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"转换为灰度图失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def adjust_gamma(image_source: str, gamma: float) -> str:
    """调整图片伽马值"""
    try:
        result = safe_run_async(color_adjust_gamma(image_source, gamma))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整伽马值失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# ============ 特效工具 ============

@mcp.tool()
def add_border(image_source: str, border_width: int = 10, border_color: str = "#000000", 
                   border_style: str = "solid", corner_radius: int = 10, output_format: str = "PNG") -> str:
    """为图片添加边框效果"""
    try:
        arguments = {
            "image_source": image_source,
            "border_width": border_width,
            "border_color": border_color,
            "border_style": border_style,
            "corner_radius": corner_radius,
            "output_format": output_format
        }
        result = safe_run_async(effects_add_border(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"添加边框失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def create_silhouette(image_source: str, silhouette_color: str = "#000000", 
                          background_color: str = "transparent", threshold: int = 128, 
                          output_format: str = "PNG") -> str:
    """创建图片的剪影效果"""
    try:
        arguments = {
            "image_source": image_source,
            "silhouette_color": silhouette_color,
            "background_color": background_color,
            "threshold": threshold,
            "output_format": output_format
        }
        result = safe_run_async(effects_create_silhouette(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"创建剪影失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def add_shadow(image_source: str, shadow_color: str = "#808080", shadow_offset_x: int = 5,
                   shadow_offset_y: int = 5, shadow_blur: int = 5, shadow_opacity: float = 0.5,
                   output_format: str = "PNG") -> str:
    """为图片添加阴影效果"""
    try:
        arguments = {
            "image_source": image_source,
            "shadow_color": shadow_color,
            "shadow_offset_x": shadow_offset_x,
            "shadow_offset_y": shadow_offset_y,
            "shadow_blur": shadow_blur,
            "shadow_opacity": shadow_opacity,
            "output_format": output_format
        }
        result = safe_run_async(effects_add_shadow(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"添加阴影失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def add_watermark(image_source: str, watermark_text: str = None, watermark_image: str = None,
                      position: str = "bottom-right", opacity: float = 0.5, scale: float = 1.0,
                      output_format: str = "PNG") -> str:
    """为图片添加水印"""
    try:
        arguments = {
            "image_source": image_source,
            "position": position,
            "opacity": opacity,
            "scale": scale,
            "output_format": output_format
        }
        if watermark_text:
            arguments["watermark_text"] = watermark_text
        if watermark_image:
            arguments["watermark_image"] = watermark_image
            
        result = safe_run_async(effects_add_watermark(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"添加水印失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def apply_vignette(image_source: str, strength: float = 0.5, output_format: str = "PNG") -> str:
    """应用晕影效果"""
    try:
        arguments = {
            "image_source": image_source,
            "strength": strength,
            "output_format": output_format
        }
        result = safe_run_async(effects_apply_vignette(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"应用晕影效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def create_polaroid(image_source: str, border_width: int = 20, shadow: bool = True,
                        output_format: str = "PNG") -> str:
    """创建宝丽来风格效果"""
    try:
        arguments = {
            "image_source": image_source,
            "border_width": border_width,
            "shadow": shadow,
            "output_format": output_format
        }
        result = safe_run_async(effects_create_polaroid(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"创建宝丽来效果失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# ============ 高级工具 ============

@mcp.tool()
def batch_resize(image_sources: list, target_width: int, target_height: int, 
                     keep_aspect_ratio: bool = True, output_format: str = "PNG") -> str:
    """批量调整图片大小"""
    try:
        arguments = {
            "image_sources": image_sources,
            "target_width": target_width,
            "target_height": target_height,
            "keep_aspect_ratio": keep_aspect_ratio,
            "output_format": output_format
        }
        result = safe_run_async(advanced_batch_resize(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"批量调整大小失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def create_collage(image_sources: list, layout: str = "grid", spacing: int = 10,
                       background_color: str = "#FFFFFF", output_format: str = "PNG") -> str:
    """创建图片拼贴"""
    try:
        arguments = {
            "image_sources": image_sources,
            "layout": layout,
            "spacing": spacing,
            "background_color": background_color,
            "output_format": output_format
        }
        result = safe_run_async(advanced_create_collage(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"创建拼贴失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def create_thumbnail_grid(image_sources: list, thumbnail_size: int = 150, 
                              grid_columns: int = 4, spacing: int = 10,
                              background_color: str = "#FFFFFF", output_format: str = "PNG") -> str:
    """创建缩略图网格"""
    try:
        arguments = {
            "image_sources": image_sources,
            "thumbnail_size": thumbnail_size,
            "grid_columns": grid_columns,
            "spacing": spacing,
            "background_color": background_color,
            "output_format": output_format
        }
        result = safe_run_async(advanced_create_thumbnail_grid(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"创建缩略图网格失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def blend_images(image1_source: str, image2_source: str, blend_mode: str = "normal",
                     opacity: float = 0.5, output_format: str = "PNG") -> str:
    """混合两张图片"""
    try:
        arguments = {
            "image1_source": image1_source,
            "image2_source": image2_source,
            "blend_mode": blend_mode,
            "opacity": opacity,
            "output_format": output_format
        }
        result = safe_run_async(advanced_blend_images(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"混合图片失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def extract_colors(image_source: str, num_colors: int = 5, output_format: str = "PNG") -> str:
    """提取图片主要颜色"""
    try:
        arguments = {
            "image_source": image_source,
            "num_colors": num_colors,
            "output_format": output_format
        }
        result = safe_run_async(advanced_extract_colors(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"提取颜色失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def create_gif(image_sources: list, duration: int = 500, loop: int = 0) -> str:
    """创建GIF动画"""
    try:
        arguments = {
            "image_sources": image_sources,
            "duration": duration,
            "loop": loop
        }
        result = safe_run_async(advanced_create_gif(arguments))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"创建GIF失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_performance_stats() -> str:
    """获取性能统计信息"""
    try:
        stats = utils_get_performance_stats()
        return json.dumps({
            "success": True,
            "data": stats
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"获取性能统计失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def reset_performance_stats() -> str:
    """重置性能统计信息"""
    try:
        utils_reset_performance_stats()
        return json.dumps({
            "success": True,
            "message": "性能统计已重置"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"重置性能统计失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(f"start PS-MCP server...",file=sys.stderr)
    mcp.run()