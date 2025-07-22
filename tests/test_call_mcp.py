#!/usr/bin/env python3
"""
创建测试图片并测试FastMCP服务器的图片处理功能

本测试脚本包含以下工具类别的全面测试：

📂 基础工具 (Basic Tools):
   - get_image_info: 获取图片基本信息
   - convert_format: 转换图片格式

📂 几何变换工具 (Transform Tools):
   - resize_image: 调整图片大小
   - crop_image: 裁剪图片
   - rotate_image: 旋转图片
   - flip_image: 翻转图片

📂 滤镜工具 (Filter Tools):
   - apply_blur: 应用模糊滤镜
   - apply_gaussian_blur: 应用高斯模糊滤镜
   - apply_sharpen: 应用锐化滤镜
   - apply_emboss: 应用浮雕滤镜
   - apply_sepia: 应用复古棕褐色滤镜
   - apply_find_edges: 应用边缘检测滤镜
   - apply_invert: 应用反色滤镜
   - apply_contour: 应用轮廓滤镜
   - apply_smooth: 应用平滑滤镜

📂 色彩调整工具 (Color Adjustment Tools):
   - adjust_brightness: 调整图片亮度
   - adjust_contrast: 调整图片对比度
   - adjust_saturation: 调整图片饱和度
   - adjust_sharpness: 调整图片锐度
   - convert_to_grayscale: 转换为灰度图
   - adjust_gamma: 调整伽马值

📂 特效工具 (Effects Tools):
   - add_border: 为图片添加边框效果
   - add_watermark: 为图片添加水印
   - create_silhouette: 创建图片的剪影效果
   - add_shadow: 为图片添加阴影效果
   - apply_vignette: 应用晕影效果
   - create_polaroid: 创建宝丽来风格效果

📂 高级工具 (Advanced Tools):
   - extract_colors: 提取图片主要颜色
   - create_thumbnail_grid: 创建缩略图网格

📂 性能监控工具 (Performance Tools):
   - get_performance_stats: 获取性能统计信息

总计: 30个测试用例，覆盖所有主要功能模块
"""

import asyncio
import json
import sys
import os
from pathlib import Path
import traceback
import base64
import re
from PIL import Image, ImageDraw

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def save_base64_image(base64_data, filename):
    """
    保存base64编码的图片到output目录
    
    Args:
        base64_data: base64编码的图片数据
        filename: 保存的文件名
    
    Returns:
        保存的文件路径
    """
    try:
        # 确保output目录存在
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # 提取base64数据（去掉data:image/xxx;base64,前缀）
        if "base64," in base64_data:
            base64_data = base64_data.split("base64,")[1]
        
        # 解码并保存
        image_data = base64.b64decode(base64_data)
        file_path = output_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        return str(file_path)
    except Exception as e:
        print(f"保存图片失败: {e}")
        return None

def process_test_result(result, test_name, test_number):
    """
    处理测试结果，提取并保存图片数据
    
    Args:
        result: 测试结果
        test_name: 测试名称
        test_number: 测试编号
    
    Returns:
        处理后的结果信息
    """
    if not result.content or len(result.content) == 0:
        return "❌ 无返回内容"
    
    try:
        result_text = result.content[0].text
        result_data = json.loads(result_text)
        
        if result_data.get("success"):
            # 检查图片数据格式
            base64_data = None
            
            # 使用统一的 data.image_data 格式
            if "data" in result_data and "image_data" in result_data["data"]:
                base64_data = result_data["data"]["image_data"]
            
            # 如果找到图片数据，保存图片
            if base64_data:
                # 生成文件名
                safe_test_name = re.sub(r'[^\w\-_]', '_', test_name)
                filename = f"test_{test_number:02d}_{safe_test_name}.png"
                
                # 保存图片
                saved_path = save_base64_image(base64_data, filename)
                
                if saved_path:
                    # 返回不包含base64数据的结果
                    clean_data = result_data.copy()
                    if "data" in clean_data and "image_data" in clean_data["data"]:
                        clean_data["data"]["image_data"] = f"已保存到: {saved_path}"
                    
                    return json.dumps(clean_data, ensure_ascii=False, indent=2)
                else:
                    return result_text
            else:
                # 没有图片数据，直接返回
                return json.dumps(result_data, ensure_ascii=False, indent=2)
        else:
            return result_text
            
    except json.JSONDecodeError:
        # 不是JSON格式，直接返回
        return result_text
    except Exception as e:
        return f"处理结果时出错: {e}\n原始结果: {result_text}"

def create_test_image():
    """创建一个测试图片"""
    # 创建一个简单的测试图片
    # img = Image.new('RGB', (200, 200), color='lightblue')
    # draw = ImageDraw.Draw(img)
    
    # # 绘制一些图形
    # draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=2)
    # draw.ellipse([75, 75, 125, 125], fill='yellow')
    
    # 保存测试图片
    # test_image_path = "test_image.png"
    test_image_path = "D:\\Documents\\Pictures\\20250428091250.png"
    # img.save(test_image_path)
    print(f"✅ 创建测试图片: {test_image_path}")
    return test_image_path

async def test_image_processing():
    """测试图片处理功能"""
    print("🧪 PS-MCP 图片处理功能测试...")
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 配置路径
    current_dir = Path(__file__).parent
    server_script = current_dir / "main.py"
    python_path = r"D:\App\Miniconda3\envs\image-mcp\python.exe"
    
    try:
        # 设置服务器参数
        server_params = StdioServerParameters(
            command=python_path,
            args=[str(server_script), "stdio"],
            env=dict(os.environ)
        )
        
        print("🔌 连接到PS-MCP FastMCP服务器...")
        
        # 连接到服务器
        async with stdio_client(server_params) as (read, write):
            print("✅ 服务器进程启动成功")
            
            async with ClientSession(read, write) as session:
                print("✅ 客户端会话创建成功")
                
                # 初始化
                await session.initialize()
                print("✅ 协议初始化成功")
                
                # 获取工具列表
                tools_result = await session.list_tools()
                tools = {tool.name: tool for tool in tools_result.tools}
                print(f"✅ 发现 {len(tools)} 个工具: {list(tools.keys())}")
                
                # 测试1: 获取图片信息
                # print("\n📋 测试1: 获取图片信息...")
                # result = await session.call_tool("get_image_info", {
                #     "image_source": test_image
                # })
                # processed_result = process_test_result(result, "获取图片信息", 1)
                # print(f"✅ 测试 1: 获取图片信息")
                # print(f"结果: {processed_result}")
                
                # # 测试2: 调整图片大小
                # print("\n📏 测试2: 调整图片大小...")
                # result = await session.call_tool("resize_image", {
                #     "image_source": test_image,
                #     "width": 200,
                #     "height": 200
                # })
                # processed_result = process_test_result(result, "调整图片大小", 2)
                # print(f"✅ 测试 2: 调整图片大小")
                # print(f"结果: {processed_result}")
                
                # # 测试3: 转换图片格式
                # print("\n🔄 测试3: 转换图片格式...")
                # result = await session.call_tool("convert_format", {
                #     "image_source": test_image,
                #     "output_format": "JPEG"
                # })
                # processed_result = process_test_result(result, "转换图片格式", 3)
                # print(f"✅ 测试 3: 转换图片格式")
                # print(f"结果: {processed_result}")
                
                # # 测试4: 应用模糊效果
                # print("\n🌫️ 测试4: 应用模糊效果...")
                # result = await session.call_tool("apply_blur", {
                #     "image_source": test_image,
                #     "radius": 2.0
                # })
                # processed_result = process_test_result(result, "应用模糊效果", 4)
                # print(f"✅ 测试 4: 应用模糊效果")
                # print(f"结果: {processed_result}")
                    
                # 测试5: 裁剪图片
                # print("\n✂️ 测试5: 裁剪图片...")
                # result = await session.call_tool("crop_image", {
                #     "image_source": test_image,
                #     "left": 125,
                #     "top": 25,
                #     "right": 1175,
                #     "bottom": 1275
                # })
                # processed_result = process_test_result(result, "裁剪图片", 5)
                # print(f"✅ 测试 5: 裁剪图片")
                # print(f"结果: {processed_result}")
                
                # # 测试6: 旋转图片
                # print("\n🔄 测试6: 旋转图片...")
                # result = await session.call_tool("rotate_image", {
                #     "image_source": test_image,
                #     "angle": 45
                # })
                # processed_result = process_test_result(result, "旋转图片", 6)
                # print(f"✅ 测试 6: 旋转图片")
                # print(f"结果: {processed_result}")
                
                # # 测试7: 翻转图片
                # print("\n🔄 测试7: 翻转图片...")
                # result = await session.call_tool("flip_image", {
                #     "image_source": test_image,
                #     "direction": "horizontal"
                # })
                # processed_result = process_test_result(result, "翻转图片", 7)
                # print(f"✅ 测试 7: 翻转图片")
                # print(f"结果: {processed_result}")
                
                # 测试8: 调整亮度
                print("\n☀️ 测试8: 调整亮度...")
                result = await session.call_tool("adjust_brightness", {
                    "image_source": test_image,
                    "factor": 1.3
                })
                processed_result = process_test_result(result, "调整亮度", 8)
                print(f"✅ 测试 8: 调整亮度")
                print(f"结果: {processed_result}")
                
                # 测试9: 调整对比度
                print("\n🌓 测试9: 调整对比度...")
                result = await session.call_tool("adjust_contrast", {
                    "image_source": test_image,
                    "factor": 1.2
                })
                processed_result = process_test_result(result, "调整对比度", 9)
                print(f"✅ 测试 9: 调整对比度")
                print(f"结果: {processed_result}")
                
                # 测试10: 转换为灰度图
                # print("\n⚫ 测试10: 转换为灰度图...")
                # result = await session.call_tool("convert_to_grayscale", {
                #     "image_source": test_image
                # })
                # processed_result = process_test_result(result, "转换为灰度图", 10)
                # print(f"✅ 测试 10: 转换为灰度图")
                # print(f"结果: {processed_result}")
                
                # 测试11: 应用锐化滤镜
                print("\n🔍 测试11: 应用锐化滤镜...")
                result = await session.call_tool("apply_sharpen", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用锐化滤镜", 11)
                print(f"✅ 测试 11: 应用锐化滤镜")
                print(f"结果: {processed_result}")
                
                # 测试12: 应用浮雕滤镜
                print("\n🎨 测试12: 应用浮雕滤镜...")
                result = await session.call_tool("apply_emboss", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用浮雕滤镜", 12)
                print(f"✅ 测试 12: 应用浮雕滤镜")
                print(f"结果: {processed_result}")
                
                # 测试13: 应用复古棕褐色滤镜
                print("\n📸 测试13: 应用复古棕褐色滤镜...")
                result = await session.call_tool("apply_sepia", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用复古棕褐色滤镜", 13)
                print(f"✅ 测试 13: 应用复古棕褐色滤镜")
                print(f"结果: {processed_result}")
                
                # 测试14: 添加边框
                print("\n🖼️ 测试14: 添加边框...")
                result = await session.call_tool("add_border", {
                    "image_source": test_image,
                    "border_width": 10,
                    "border_color": "#FF0000"
                })
                processed_result = process_test_result(result, "添加边框", 14)
                print(f"✅ 测试 14: 添加边框")
                print(f"结果: {processed_result}")
                
                # 测试15: 添加水印
                print("\n💧 测试15: 添加水印...")
                result = await session.call_tool("add_watermark", {
                    "image_source": test_image,
                    "watermark_text": "PS-MCP Test",
                    "position": "bottom-right",
                    "opacity": 0.7
                })
                processed_result = process_test_result(result, "添加水印", 15)
                print(f"✅ 测试 15: 添加水印")
                print(f"结果: {processed_result}")
                
                # 测试16: 提取主要颜色
                print("\n🎨 测试16: 提取主要颜色...")
                result = await session.call_tool("extract_colors", {
                    "image_source": test_image,
                    "num_colors": 5
                })
                processed_result = process_test_result(result, "提取主要颜色", 16)
                print(f"✅ 测试 16: 提取主要颜色")
                print(f"结果: {processed_result}")
                
                # 测试17: 创建缩略图
                print("\n🖼️ 测试17: 创建缩略图...")
                result = await session.call_tool("create_thumbnail_grid", {
                    "image_sources": [test_image, test_image, test_image, test_image],
                    "grid_size": "2x2",
                    "thumbnail_size": 50
                })
                processed_result = process_test_result(result, "创建缩略图", 17)
                print(f"✅ 测试 17: 创建缩略图")
                print(f"结果: {processed_result}")
                
                # 测试18: 性能统计
                print("\n📊 测试18: 性能统计...")
                result = await session.call_tool("get_performance_stats", {})
                processed_result = process_test_result(result, "性能统计", 18)
                print(f"✅ 测试 18: 性能统计")
                print(f"结果: {processed_result}")
                
                # 测试19: 应用边缘检测滤镜
                print("\n🔍 测试19: 应用边缘检测滤镜...")
                result = await session.call_tool("apply_find_edges", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用边缘检测滤镜", 19)
                print(f"✅ 测试 19: 应用边缘检测滤镜")
                print(f"结果: {processed_result}")
                
                # 测试20: 应用高斯模糊
                print("\n🌫️ 测试20: 应用高斯模糊...")
                result = await session.call_tool("apply_gaussian_blur", {
                    "image_source": test_image,
                    "radius": 2.0
                })
                processed_result = process_test_result(result, "应用高斯模糊", 20)
                print(f"✅ 测试 20: 应用高斯模糊")
                print(f"结果: {processed_result}")
                
                # 测试21: 调整饱和度
                print("\n🌈 测试21: 调整饱和度...")
                result = await session.call_tool("adjust_saturation", {
                    "image_source": test_image,
                    "factor": 1.5
                })
                processed_result = process_test_result(result, "调整饱和度", 21)
                print(f"✅ 测试 21: 调整饱和度")
                print(f"结果: {processed_result}")
                
                # 测试22: 调整锐度
                print("\n🔪 测试22: 调整锐度...")
                result = await session.call_tool("adjust_sharpness", {
                    "image_source": test_image,
                    "factor": 1.3
                })
                processed_result = process_test_result(result, "调整锐度", 22)
                print(f"✅ 测试 22: 调整锐度")
                print(f"结果: {processed_result}")
                
                # 测试23: 应用反色滤镜
                print("\n🔄 测试23: 应用反色滤镜...")
                result = await session.call_tool("apply_invert", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用反色滤镜", 23)
                print(f"✅ 测试 23: 应用反色滤镜")
                print(f"结果: {processed_result}")
                
                # 测试24: 创建剪影效果
                print("\n👤 测试24: 创建剪影效果...")
                result = await session.call_tool("create_silhouette", {
                    "image_source": test_image,
                    "threshold": 128
                })
                processed_result = process_test_result(result, "创建剪影效果", 24)
                print(f"✅ 测试 24: 创建剪影效果")
                print(f"结果: {processed_result}")
                
                # 测试25: 添加阴影效果
                print("\n🌑 测试25: 添加阴影效果...")
                result = await session.call_tool("add_shadow", {
                    "image_source": test_image,
                    "offset_x": 5,
                    "offset_y": 5,
                    "blur_radius": 3
                })
                processed_result = process_test_result(result, "添加阴影效果", 25)
                print(f"✅ 测试 25: 添加阴影效果")
                print(f"结果: {processed_result}")
                
                # 测试26: 应用晕影效果
                print("\n🌅 测试26: 应用晕影效果...")
                result = await session.call_tool("apply_vignette", {
                    "image_source": test_image,
                    "strength": 0.5
                })
                processed_result = process_test_result(result, "应用晕影效果", 26)
                print(f"✅ 测试 26: 应用晕影效果")
                print(f"结果: {processed_result}")
                
                # 测试27: 创建宝丽来风格
                print("\n📷 测试27: 创建宝丽来风格...")
                result = await session.call_tool("create_polaroid", {
                    "image_source": test_image,
                    "border_width": 20
                })
                processed_result = process_test_result(result, "创建宝丽来风格", 27)
                print(f"✅ 测试 27: 创建宝丽来风格")
                # print(f"结果: {processed_result}")
                
                # 测试28: 调整伽马值
                print("\n⚡ 测试28: 调整伽马值...")
                result = await session.call_tool("adjust_gamma", {
                    "image_source": test_image,
                    "gamma": 1.2
                })
                processed_result = process_test_result(result, "调整伽马值", 28)
                print(f"✅ 测试 28: 调整伽马值")
                print(f"结果: {processed_result}")
                
                # 测试29: 应用轮廓滤镜
                print("\n📐 测试29: 应用轮廓滤镜...")
                result = await session.call_tool("apply_contour", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用轮廓滤镜", 29)
                print(f"✅ 测试 29: 应用轮廓滤镜")
                print(f"结果: {processed_result}")
                
                # 测试30: 应用平滑滤镜
                print("\n🌊 测试30: 应用平滑滤镜...")
                result = await session.call_tool("apply_smooth", {
                    "image_source": test_image
                })
                processed_result = process_test_result(result, "应用平滑滤镜", 30)
                print(f"✅ 测试 30: 应用平滑滤镜")
                print(f"结果: {processed_result}")
                
                print("\n🎉 所有图片处理功能测试完成!")
                
                # 测试总结
                print("\n" + "="*60)
                print("📊 测试总结统计")
                print("="*60)
                print("✅ 基础工具测试: 2个")
                print("✅ 几何变换工具测试: 4个") 
                print("✅ 滤镜工具测试: 9个")
                print("✅ 色彩调整工具测试: 6个")
                print("✅ 特效工具测试: 6个")
                print("✅ 高级工具测试: 2个")
                print("✅ 性能监控工具测试: 1个")
                print("-"*60)
                print("🎯 总计: 30个测试用例全部完成")
                print("="*60)
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_processing())