# -*- coding: utf-8 -*-
"""
图片编辑模块
提供图片区域覆盖和文字绘制功能
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import platform


def get_chinese_font(size: int = 24):
    """
    获取支持中文的字体
    
    Args:
        size: 字体大小
    
    Returns:
        ImageFont 对象
    """
    system = platform.system()
    
    # 不同系统的中文字体路径
    font_paths = []
    
    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    
    # 如果都找不到，返回默认字体
    print("警告: 未找到中文字体，使用默认字体")
    return ImageFont.load_default()


def edit_region(
    image: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int,
    new_text: str,
    bg_color: str = "white",
    text_color: str = "red",
    font_size: int = 24
) -> Image.Image:
    """
    修改图片中的指定区域
    
    Args:
        image: PIL Image 对象
        x, y: 区域左上角坐标
        width, height: 区域宽高
        new_text: 新的文字内容
        bg_color: 背景色
        text_color: 文字颜色
        font_size: 字体大小
    
    Returns:
        修改后的 Image 对象
    """
    img = image.copy()
    draw = ImageDraw.Draw(img)
    font = get_chinese_font(font_size)
    
    # 用背景色覆盖原区域
    draw.rectangle([x, y, x + width, y + height], fill=bg_color)
    
    # 计算文字位置（垂直居中）
    text_bbox = draw.textbbox((0, 0), new_text, font=font)
    text_height = text_bbox[3] - text_bbox[1]
    text_y = y + (height - text_height) // 2
    
    # 绘制新文字
    draw.text((x + 5, text_y), new_text, fill=text_color, font=font)
    
    return img


def add_watermark(
    image: Image.Image,
    text: str = "仅供内部培训使用",
    position: str = "top-left",
    opacity: int = 128
) -> Image.Image:
    """
    添加水印
    
    Args:
        image: PIL Image 对象
        text: 水印文字
        position: 位置 (top-left, top-right, bottom-left, bottom-right, center)
        opacity: 透明度 (0-255)
    
    Returns:
        添加水印后的 Image 对象
    """
    img = image.copy().convert("RGBA")
    
    # 创建水印层
    watermark = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    font = get_chinese_font(20)
    
    # 计算文字大小
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # 计算位置
    padding = 10
    if position == "top-left":
        pos = (padding, padding)
    elif position == "top-right":
        pos = (img.width - text_width - padding, padding)
    elif position == "bottom-left":
        pos = (padding, img.height - text_height - padding)
    elif position == "bottom-right":
        pos = (img.width - text_width - padding, img.height - text_height - padding)
    else:  # center
        pos = ((img.width - text_width) // 2, (img.height - text_height) // 2)
    
    # 绘制半透明水印
    draw.text(pos, text, fill=(128, 128, 128, opacity), font=font)
    
    # 合并图层
    result = Image.alpha_composite(img, watermark)
    return result.convert("RGB")


def save_image(image: Image.Image, output_path: str, quality: int = 95):
    """
    保存图片
    
    Args:
        image: PIL Image 对象
        output_path: 输出路径
        quality: JPEG 质量 (1-100)
    """
    output_file = Path(output_path)
    
    # 根据扩展名保存
    if output_file.suffix.lower() in ['.jpg', '.jpeg']:
        image.save(output_path, 'JPEG', quality=quality)
    else:
        image.save(output_path, 'PNG')
    
    print(f"图片已保存: {output_file.absolute()}")


if __name__ == "__main__":
    # 测试
    img = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), "原始文字", fill="black", font=get_chinese_font(30))
    
    # 修改区域
    img = edit_region(img, 100, 100, 200, 50, "¥999.00", "white", "red", 30)
    img = add_watermark(img, "测试水印")
    save_image(img, "test_edit.png")





