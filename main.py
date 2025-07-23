#!/usr/bin/env python3
"""
使用FastMCP的PS-MCP图片处理服务器 - 主程序
集成所有tools目录下的工具方法
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Annotated, Union
import json
import traceback
import asyncio
from pydantic import Field

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
    adjust_gamma as color_adjust_gamma,
    adjust_opacity as color_adjust_opacity
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
def load_image(
    source: Annotated[str, Field(description="图片文件路径或base64编码的图片数据。支持本地文件路径（如 'image.jpg'）或base64编码字符串")]
) -> str:
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
def save_image(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    output_path: Annotated[str, Field(description="输出文件路径，包含文件名和扩展名（如 'output.png'）")],
    format: Annotated[str, Field(description="图片格式，支持 PNG、JPEG、WEBP、BMP、TIFF 等", default="PNG")],
    quality: Annotated[int, Field(description="图片质量，范围 1-100，仅对 JPEG 格式有效", ge=1, le=100, default=95)]
) -> str:
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
def get_image_info(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def convert_format(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    target_format: Annotated[str, Field(description="目标格式：PNG、JPEG、WEBP、BMP、TIFF、GIF 等")],
    quality: Annotated[int, Field(description="图片质量，范围 1-100，仅对 JPEG 格式有效", ge=1, le=100, default=95)]
) -> str:
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
def resize_image(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    width: Annotated[int, Field(description="目标宽度（像素）", gt=0)],
    height: Annotated[int, Field(description="目标高度（像素）", gt=0)],
    keep_aspect_ratio: Annotated[bool, Field(description="是否保持宽高比，True时会按比例缩放", default=True)],
    resample: Annotated[str, Field(description="重采样算法：LANCZOS（高质量）、BILINEAR（平滑）、NEAREST（快速）", default="LANCZOS")]
) -> str:
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
def crop_image(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    left: Annotated[int, Field(description="裁剪区域左边界坐标（像素）", ge=0)],
    top: Annotated[int, Field(description="裁剪区域上边界坐标（像素）", ge=0)],
    right: Annotated[int, Field(description="裁剪区域右边界坐标（像素）", gt=0)],
    bottom: Annotated[int, Field(description="裁剪区域下边界坐标（像素）", gt=0)]
) -> str:
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
def rotate_image(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    angle: Annotated[float, Field(description="旋转角度（度），正值为顺时针，负值为逆时针")],
    expand: Annotated[bool, Field(description="是否扩展画布以容纳旋转后的图片，False会裁剪", default=True)],
    fill_color: Annotated[str, Field(description="填充颜色，十六进制格式如 #FFFFFF（白色）", default="#FFFFFF")]
) -> str:
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
def flip_image(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    direction: Annotated[str, Field(description="翻转方向：horizontal（水平翻转）或 vertical（垂直翻转）")]
) -> str:
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
def apply_blur(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    radius: Annotated[float, Field(description="模糊半径，值越大模糊效果越强", ge=0.1)]
) -> str:
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
def apply_gaussian_blur(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    radius: Annotated[float, Field(description="高斯模糊半径，值越大模糊效果越强", ge=0.1)]
) -> str:
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
def apply_sharpen(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_edge_enhance(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_emboss(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_find_edges(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_smooth(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_contour(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_sepia(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def apply_invert(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def adjust_brightness(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    factor: Annotated[float, Field(description="亮度调整因子，1.0为原始亮度，>1.0变亮，<1.0变暗", gt=0)]
) -> str:
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
def adjust_contrast(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    factor: Annotated[float, Field(description="对比度调整因子，1.0为原始对比度，>1.0增强，<1.0减弱", gt=0)]
) -> str:
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
def adjust_saturation(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    factor: Annotated[float, Field(description="饱和度调整因子，1.0为原始饱和度，>1.0增强，<1.0减弱，0为灰度", ge=0)]
) -> str:
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
def adjust_sharpness(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    factor: Annotated[float, Field(description="锐度调整因子，1.0为原始锐度，>1.0增强，<1.0减弱", gt=0)]
) -> str:
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
def convert_to_grayscale(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")]
) -> str:
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
def adjust_gamma(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    gamma: Annotated[float, Field(description="伽马值，1.0为原始，>1.0变亮，<1.0变暗", gt=0)]
) -> str:
    """调整图片伽马值"""
    try:
        result = safe_run_async(color_adjust_gamma(image_source, gamma))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整伽马值失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def adjust_opacity(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    opacity: Annotated[float, Field(description="不透明度，范围 0.0-1.0，0.0为完全透明，1.0为完全不透明", ge=0.0, le=1.0)]
) -> str:
    """调整图片不透明度"""
    try:
        result = safe_run_async(color_adjust_opacity(image_source, opacity))
        return result[0].text
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"调整不透明度失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# ============ 特效工具 ============

@mcp.tool()
def add_border(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    border_width: Annotated[int, Field(description="边框宽度（像素）", ge=1, default=10)],
    border_color: Annotated[str, Field(description="边框颜色，十六进制格式如 #000000（黑色）", default="#000000")],
    border_style: Annotated[str, Field(description="边框样式：solid（实线）、dashed（虚线）、dotted（点线）", default="solid")],
    corner_radius: Annotated[int, Field(description="圆角半径（像素），0为直角", ge=0, default=10)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def create_silhouette(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    silhouette_color: Annotated[str, Field(description="剪影颜色，十六进制格式如 #000000（黑色）", default="#000000")],
    background_color: Annotated[str, Field(description="背景颜色，十六进制格式或 'transparent'（透明）", default="transparent")],
    threshold: Annotated[int, Field(description="阈值，范围 0-255，用于确定剪影边界", ge=0, le=255, default=128)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def add_shadow(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    shadow_color: Annotated[str, Field(description="阴影颜色，十六进制格式如 #808080（灰色）", default="#808080")],
    shadow_offset_x: Annotated[int, Field(description="阴影水平偏移（像素），正值向右，负值向左", default=5)],
    shadow_offset_y: Annotated[int, Field(description="阴影垂直偏移（像素），正值向下，负值向上", default=5)],
    shadow_blur: Annotated[int, Field(description="阴影模糊半径（像素）", ge=0, default=5)],
    shadow_opacity: Annotated[float, Field(description="阴影不透明度，范围 0.0-1.0", ge=0.0, le=1.0, default=0.5)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def add_watermark(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    watermark_text: Annotated[Optional[str], Field(description="水印文字内容，与watermark_image二选一", default=None)],
    watermark_image: Annotated[Optional[str], Field(description="水印图片路径或base64数据，与watermark_text二选一", default=None)],
    position: Annotated[str, Field(description="水印位置：top-left、top-right、bottom-left、bottom-right、center", default="bottom-right")],
    opacity: Annotated[float, Field(description="水印不透明度，范围 0.0-1.0", ge=0.0, le=1.0, default=0.5)],
    scale: Annotated[float, Field(description="水印缩放比例，1.0为原始大小", gt=0, default=1.0)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def apply_vignette(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    strength: Annotated[float, Field(description="晕影强度，范围 0.0-1.0，值越大效果越明显", ge=0.0, le=1.0, default=0.5)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def create_polaroid(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    border_width: Annotated[int, Field(description="宝丽来边框宽度（像素）", ge=1, default=20)],
    shadow: Annotated[bool, Field(description="是否添加阴影效果", default=True)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def batch_resize(
    image_sources: Annotated[list, Field(description="图片源列表，每个元素可以是文件路径或base64编码的图片数据")],
    target_width: Annotated[int, Field(description="目标宽度（像素）", ge=1)],
    target_height: Annotated[int, Field(description="目标高度（像素）", ge=1)],
    keep_aspect_ratio: Annotated[bool, Field(description="是否保持宽高比", default=True)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def create_collage(
    image_sources: Annotated[list, Field(description="图片源列表，每个元素可以是文件路径或base64编码的图片数据")],
    layout: Annotated[str, Field(description="布局方式：grid（网格）、horizontal（水平）、vertical（垂直）", default="grid")],
    spacing: Annotated[int, Field(description="图片间距（像素）", ge=0, default=10)],
    background_color: Annotated[str, Field(description="背景颜色，支持十六进制颜色代码", default="#FFFFFF")],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def create_thumbnail_grid(
    image_sources: Annotated[list, Field(description="图片源列表，每个元素可以是文件路径或base64编码的图片数据")],
    thumbnail_size: Annotated[int, Field(description="缩略图大小（像素）", ge=50, default=150)],
    grid_columns: Annotated[int, Field(description="网格列数", ge=1, default=4)],
    spacing: Annotated[int, Field(description="图片间距（像素）", ge=0, default=10)],
    background_color: Annotated[str, Field(description="背景颜色，支持十六进制颜色代码", default="#FFFFFF")],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def blend_images(
    image1_source: Annotated[str, Field(description="第一张图片源，可以是文件路径或base64编码的图片数据")],
    image2_source: Annotated[str, Field(description="第二张图片源，可以是文件路径或base64编码的图片数据")],
    blend_mode: Annotated[str, Field(description="混合模式：normal（正常）、multiply（正片叠底）、screen（滤色）、overlay（叠加）", default="normal")],
    opacity: Annotated[float, Field(description="第二张图片的不透明度，范围 0.0-1.0", ge=0.0, le=1.0, default=0.5)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def extract_colors(
    image_source: Annotated[str, Field(description="图片源，可以是文件路径或base64编码的图片数据")],
    num_colors: Annotated[int, Field(description="要提取的主要颜色数量", ge=1, le=20, default=5)],
    output_format: Annotated[str, Field(description="输出格式：PNG、JPEG、WEBP 等", default="PNG")]
) -> str:
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
def create_gif(
    image_sources: Annotated[list, Field(description="图片源列表，每个元素可以是文件路径或base64编码的图片数据")],
    duration: Annotated[int, Field(description="每帧持续时间（毫秒）", ge=50, default=500)],
    loop: Annotated[int, Field(description="循环次数，0表示无限循环", ge=0, default=0)]
) -> str:
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

def main():
    """主程序入口点，用于 uv 脚本运行"""
    print("start PS-MCP image server...", file=sys.stderr)
    mcp.run()

if __name__ == "__main__":
    main()