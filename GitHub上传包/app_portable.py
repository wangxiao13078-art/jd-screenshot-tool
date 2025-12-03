# -*- coding: utf-8 -*-
"""
京东截图编辑工具 - 便携版
只保留图片编辑功能，无需浏览器依赖
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
from pathlib import Path
import platform
import sys
import os


def get_chinese_font(size: int = 24):
    """获取中文字体"""
    system = platform.system()
    font_paths = []
    
    if system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    
    return ImageFont.load_default()


class ScreenshotEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("京东截图编辑工具 - 便携版")
        self.root.geometry("1200x800")
        
        # 状态变量
        self.original_image = None
        self.current_image = None
        self.photo_image = None
        self.scale = 1.0
        
        # 框选相关
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.edit_count = 0
        
        self._create_ui()
    
    def _create_ui(self):
        """创建界面"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="📂 打开图片", command=self._open_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="💾 保存图片", command=self._save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="↩️ 撤销所有", command=self._undo_all).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 编辑选项
        ttk.Label(toolbar, text="文字颜色:").pack(side=tk.LEFT, padx=5)
        self.color_var = tk.StringVar(value="red")
        colors = [("红", "red"), ("黑", "black"), ("蓝", "blue")]
        for text, color in colors:
            ttk.Radiobutton(toolbar, text=text, variable=self.color_var, value=color).pack(side=tk.LEFT)
        
        ttk.Label(toolbar, text="  字号:").pack(side=tk.LEFT, padx=5)
        self.font_size_var = tk.IntVar(value=24)
        font_combo = ttk.Combobox(toolbar, textvariable=self.font_size_var, width=4, 
                                   values=[16, 20, 24, 28, 32, 36, 40, 48])
        font_combo.pack(side=tk.LEFT)
        
        # 水印选项
        self.watermark_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="添加水印", variable=self.watermark_var).pack(side=tk.LEFT, padx=20)
        
        # 状态栏
        self.status_var = tk.StringVar(value="请先打开一张图片")
        ttk.Label(toolbar, textvariable=self.status_var, foreground="gray").pack(side=tk.RIGHT, padx=10)
        
        # 提示
        hint_frame = ttk.Frame(self.root, padding=5)
        hint_frame.pack(fill=tk.X)
        ttk.Label(hint_frame, 
                  text="💡 使用方法：打开图片 → 用鼠标框选要修改的区域 → 输入新文字 → 保存", 
                  foreground="blue").pack()
        
        # 图片显示区
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 滚动条
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            bg="#2d2d2d",
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scroll.config(command=self.canvas.xview)
        v_scroll.config(command=self.canvas.yview)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
    
    def _open_image(self):
        """打开图片"""
        file_path = filedialog.askopenfilename(
            title="选择截图",
            filetypes=[("图片", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.edit_count = 0
                self._display_image()
                self.status_var.set(f"已加载: {Path(file_path).name} ({self.original_image.width}x{self.original_image.height})")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开图片: {e}")
    
    def _display_image(self):
        """显示图片"""
        if self.current_image is None:
            return
        
        # 计算缩放
        canvas_width = self.canvas.winfo_width() or 1000
        canvas_height = self.canvas.winfo_height() or 600
        
        img_w, img_h = self.current_image.size
        scale_w = canvas_width / img_w
        scale_h = canvas_height / img_h
        self.scale = min(scale_w, scale_h, 1.0)
        
        display_w = int(img_w * self.scale)
        display_h = int(img_h * self.scale)
        
        display_img = self.current_image.copy()
        if self.scale < 1.0:
            display_img = display_img.resize((display_w, display_h), Image.Resampling.LANCZOS)
        
        self.photo_image = ImageTk.PhotoImage(display_img)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.canvas.config(scrollregion=(0, 0, display_w, display_h))
    
    def _on_mouse_down(self, event):
        """鼠标按下"""
        if self.current_image is None:
            return
        
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2, dash=(4, 4)
        )
    
    def _on_mouse_drag(self, event):
        """鼠标拖动"""
        if self.rect_id is None:
            return
        
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)
    
    def _on_mouse_up(self, event):
        """鼠标释放"""
        if self.current_image is None or self.rect_id is None:
            return
        
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # 转换回原图坐标
        x1 = int(min(self.start_x, end_x) / self.scale)
        y1 = int(min(self.start_y, end_y) / self.scale)
        x2 = int(max(self.start_x, end_x) / self.scale)
        y2 = int(max(self.start_y, end_y) / self.scale)
        
        width = x2 - x1
        height = y2 - y1
        
        if width < 10 or height < 10:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            return
        
        # 弹出输入框
        new_text = simpledialog.askstring(
            "输入新文字",
            f"选区: ({x1}, {y1}) 尺寸: {width}x{height}\n\n请输入要显示的新文字:",
            parent=self.root
        )
        
        if new_text:
            self._apply_edit(x1, y1, width, height, new_text)
        
        self.canvas.delete(self.rect_id)
        self.rect_id = None
    
    def _apply_edit(self, x, y, width, height, new_text):
        """应用编辑"""
        img = self.current_image.copy()
        draw = ImageDraw.Draw(img)
        font = get_chinese_font(self.font_size_var.get())
        
        # 覆盖原区域
        draw.rectangle([x, y, x + width, y + height], fill="white")
        
        # 绘制新文字
        text_bbox = draw.textbbox((0, 0), new_text, font=font)
        text_h = text_bbox[3] - text_bbox[1]
        text_y = y + (height - text_h) // 2
        draw.text((x + 5, text_y), new_text, fill=self.color_var.get(), font=font)
        
        self.current_image = img
        self.edit_count += 1
        self._display_image()
        self.status_var.set(f"已修改 {self.edit_count} 处")
    
    def _undo_all(self):
        """撤销所有"""
        if self.original_image is None:
            return
        
        if messagebox.askyesno("确认", "撤销所有修改？"):
            self.current_image = self.original_image.copy()
            self.edit_count = 0
            self._display_image()
            self.status_var.set("已撤销所有修改")
    
    def _save_image(self):
        """保存图片"""
        if self.current_image is None:
            messagebox.showerror("错误", "没有可保存的图片")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        
        if not file_path:
            return
        
        try:
            img = self.current_image.copy()
            
            # 添加水印
            if self.watermark_var.get():
                draw = ImageDraw.Draw(img)
                font = get_chinese_font(18)
                draw.text((10, 10), "仅供内部培训使用", fill=(180, 180, 180), font=font)
            
            img.save(file_path)
            self.status_var.set(f"已保存: {Path(file_path).name}")
            messagebox.showinfo("成功", f"图片已保存到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))


def main():
    root = tk.Tk()
    app = ScreenshotEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()

