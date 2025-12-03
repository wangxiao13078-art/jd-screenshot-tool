# -*- coding: utf-8 -*-
"""
京东截图编辑工具 - Web 界面版
使用 Gradio 创建简洁的 Web 界面
"""

import gradio as gr
from PIL import Image, ImageDraw
from pathlib import Path
import json
import os

from browser_screenshot import take_jd_screenshot
from image_editor import edit_region, add_watermark, save_image, get_chinese_font


# 全局状态
current_image = None
original_image = None
edit_history = []


def screenshot_from_url(url: str):
    """从 URL 截图"""
    global current_image, original_image, edit_history
    
    if not url or not url.startswith("http"):
        return None, "❌ 请输入有效的 URL"
    
    try:
        output_path = "temp_screenshot.png"
        take_jd_screenshot(url, output_path)
        
        original_image = Image.open(output_path)
        current_image = original_image.copy()
        edit_history = []
        
        return current_image, f"✅ 截图成功！尺寸: {current_image.width}x{current_image.height}"
    except Exception as e:
        return None, f"❌ 截图失败: {str(e)}"


def load_local_image(image):
    """加载本地图片"""
    global current_image, original_image, edit_history
    
    if image is None:
        return None, "❌ 请选择图片"
    
    original_image = image.copy()
    current_image = image.copy()
    edit_history = []
    
    return current_image, f"✅ 图片已加载！尺寸: {current_image.width}x{current_image.height}"


def apply_edit(x: int, y: int, width: int, height: int, new_text: str, 
               text_color: str, font_size: int, bg_color: str):
    """应用编辑"""
    global current_image, edit_history
    
    if current_image is None:
        return None, "❌ 请先加载图片"
    
    if width <= 0 or height <= 0:
        return current_image, "❌ 请输入有效的区域尺寸"
    
    if not new_text:
        return current_image, "❌ 请输入替换文字"
    
    try:
        current_image = edit_region(
            current_image,
            x, y, width, height,
            new_text,
            bg_color=bg_color,
            text_color=text_color,
            font_size=font_size
        )
        
        edit_history.append({
            "x": x, "y": y, "width": width, "height": height,
            "text": new_text
        })
        
        return current_image, f"✅ 已修改！共 {len(edit_history)} 处修改"
    except Exception as e:
        return current_image, f"❌ 修改失败: {str(e)}"


def undo_all():
    """撤销所有修改"""
    global current_image, original_image, edit_history
    
    if original_image is None:
        return None, "❌ 没有可撤销的修改"
    
    current_image = original_image.copy()
    edit_history = []
    return current_image, "✅ 已撤销所有修改"


def save_with_watermark(add_wm: bool):
    """保存图片（带水印）"""
    global current_image
    
    if current_image is None:
        return None, "❌ 没有可保存的图片"
    
    try:
        output_path = "edited_screenshot.png"
        img_to_save = current_image.copy()
        
        if add_wm:
            img_to_save = add_watermark(img_to_save, "仅供内部培训使用")
        
        save_image(img_to_save, output_path)
        
        return output_path, f"✅ 已保存到: {Path(output_path).absolute()}"
    except Exception as e:
        return None, f"❌ 保存失败: {str(e)}"


def create_ui():
    """创建 Gradio 界面"""
    
    with gr.Blocks() as app:
        
        gr.Markdown(
            """
            # 📸 京东截图编辑工具
            > ⚠️ 仅供内部培训、产品设计、个人存档使用
            """
        )
        
        with gr.Row():
            # 左侧：图片显示
            with gr.Column(scale=2):
                image_display = gr.Image(
                    label="当前图片",
                    type="pil",
                    interactive=False,
                    height=600
                )
                status_text = gr.Textbox(label="状态", interactive=False)
            
            # 右侧：控制面板
            with gr.Column(scale=1):
                
                # 截图区域
                with gr.Accordion("📷 截图", open=True):
                    url_input = gr.Textbox(
                        label="京东 URL",
                        placeholder="https://item.jd.com/100012345.html",
                        lines=1
                    )
                    screenshot_btn = gr.Button("🔗 从URL截图", variant="primary")
                    
                    gr.Markdown("**或者**")
                    
                    local_image = gr.Image(
                        label="上传本地图片",
                        type="pil",
                        sources=["upload"]
                    )
                    load_btn = gr.Button("📂 加载图片")
                
                # 编辑区域
                with gr.Accordion("✏️ 编辑区域", open=True):
                    gr.Markdown(
                        """
                        **提示**: 在原图上找到要修改的区域，输入坐标和尺寸
                        - 可以用截图工具测量坐标
                        - 或者用图片编辑软件查看
                        """
                    )
                    
                    with gr.Row():
                        x_input = gr.Number(label="X 坐标", value=0, precision=0)
                        y_input = gr.Number(label="Y 坐标", value=0, precision=0)
                    
                    with gr.Row():
                        w_input = gr.Number(label="宽度", value=200, precision=0)
                        h_input = gr.Number(label="高度", value=40, precision=0)
                    
                    text_input = gr.Textbox(
                        label="替换文字",
                        placeholder="¥999.00",
                        lines=1
                    )
                    
                    with gr.Row():
                        color_input = gr.Dropdown(
                            label="文字颜色",
                            choices=["red", "black", "blue", "green", "orange"],
                            value="red"
                        )
                        font_size_input = gr.Slider(
                            label="字体大小",
                            minimum=12,
                            maximum=60,
                            value=24,
                            step=2
                        )
                    
                    bg_color_input = gr.Dropdown(
                        label="背景色",
                        choices=["white", "#f5f5f5", "#fff5f5", "#f5fff5"],
                        value="white"
                    )
                    
                    apply_btn = gr.Button("✅ 应用修改", variant="primary")
                
                # 操作区域
                with gr.Accordion("💾 操作", open=True):
                    undo_btn = gr.Button("↩️ 撤销所有修改")
                    
                    watermark_checkbox = gr.Checkbox(
                        label="添加水印（仅供内部培训使用）",
                        value=True
                    )
                    save_btn = gr.Button("💾 保存图片", variant="secondary")
                    download_file = gr.File(label="下载")
        
        # 预设快捷坐标（常见京东页面位置）
        with gr.Accordion("📍 常用区域预设（参考）", open=False):
            gr.Markdown(
                """
                | 区域 | X | Y | 宽度 | 高度 |
                |------|---|---|------|------|
                | 价格区域 | 800 | 340 | 250 | 50 |
                | 评价数量 | 1050 | 340 | 100 | 30 |
                | 商品标题 | 800 | 280 | 400 | 40 |
                
                *注意: 实际坐标可能因页面不同而变化，请根据实际截图调整*
                """
            )
        
        # 事件绑定
        screenshot_btn.click(
            fn=screenshot_from_url,
            inputs=[url_input],
            outputs=[image_display, status_text]
        )
        
        load_btn.click(
            fn=load_local_image,
            inputs=[local_image],
            outputs=[image_display, status_text]
        )
        
        apply_btn.click(
            fn=apply_edit,
            inputs=[x_input, y_input, w_input, h_input, text_input, 
                   color_input, font_size_input, bg_color_input],
            outputs=[image_display, status_text]
        )
        
        undo_btn.click(
            fn=undo_all,
            inputs=[],
            outputs=[image_display, status_text]
        )
        
        save_btn.click(
            fn=save_with_watermark,
            inputs=[watermark_checkbox],
            outputs=[download_file, status_text]
        )
    
    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )

