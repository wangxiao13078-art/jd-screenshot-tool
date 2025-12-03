# -*- coding: utf-8 -*-
"""
京东截图编辑工具 - 主程序
半自动模式：截图 → 框选区域 → 修改文字 → 保存
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
from PIL import Image, ImageTk
from pathlib import Path
import threading
import os

from browser_screenshot import take_jd_screenshot
from image_editor import edit_region, add_watermark, save_image, get_chinese_font


class ScreenshotEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("京东截图编辑工具 - 内部培训专用")
        self.root.geometry("1400x900")
        
        # 状态变量
        self.original_image = None  # 原始图片
        self.current_image = None   # 当前编辑的图片
        self.photo_image = None     # Tkinter 显示用
        self.image_path = None      # 当前图片路径
        
        # 框选相关
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.selections = []  # 保存所有选区 [(x, y, w, h, text), ...]
        
        # 缩放比例（用于显示大图）
        self.scale = 1.0
        
        self._create_ui()
    
    def _create_ui(self):
        """创建界面"""
        # 顶部控制区
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)
        
        # URL 输入
        ttk.Label(control_frame, text="京东URL:").pack(side=tk.LEFT, padx=5)
        self.url_entry = ttk.Entry(control_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        self.url_entry.insert(0, "https://item.jd.com/")
        
        # 按钮
        ttk.Button(control_frame, text="截图", command=self._take_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="打开图片", command=self._open_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="保存", command=self._save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="撤销修改", command=self._undo_all).pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_label = ttk.Label(control_frame, text="就绪", foreground="green")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # 编辑选项区
        options_frame = ttk.Frame(self.root, padding=5)
        options_frame.pack(fill=tk.X)
        
        ttk.Label(options_frame, text="文字颜色:").pack(side=tk.LEFT, padx=5)
        self.color_var = tk.StringVar(value="red")
        colors = [("红色", "red"), ("黑色", "black"), ("蓝色", "blue"), ("绿色", "green")]
        for text, color in colors:
            ttk.Radiobutton(options_frame, text=text, variable=self.color_var, value=color).pack(side=tk.LEFT)
        
        ttk.Label(options_frame, text="  字体大小:").pack(side=tk.LEFT, padx=5)
        self.font_size_var = tk.IntVar(value=24)
        font_sizes = ttk.Combobox(options_frame, textvariable=self.font_size_var, width=5, 
                                   values=[16, 18, 20, 22, 24, 28, 32, 36, 40, 48])
        font_sizes.pack(side=tk.LEFT)
        
        ttk.Label(options_frame, text="  背景色:").pack(side=tk.LEFT, padx=5)
        self.bg_color_var = tk.StringVar(value="white")
        bg_colors = [("白色", "white"), ("透明(取周围)", "auto")]
        for text, color in bg_colors:
            ttk.Radiobutton(options_frame, text=text, variable=self.bg_color_var, value=color).pack(side=tk.LEFT)
        
        # 添加水印选项
        self.watermark_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="添加水印", variable=self.watermark_var).pack(side=tk.LEFT, padx=20)
        
        # 提示
        hint_frame = ttk.Frame(self.root, padding=5)
        hint_frame.pack(fill=tk.X)
        ttk.Label(hint_frame, text="💡 使用方法：输入URL截图 或 打开本地图片 → 用鼠标框选要修改的区域 → 输入新文字 → 保存", 
                  foreground="gray").pack(side=tk.LEFT)
        
        # 图片显示区（带滚动条）
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 滚动条
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 画布
        self.canvas = tk.Canvas(
            canvas_frame, 
            bg="#f0f0f0",
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
        
        # 底部信息
        info_frame = ttk.Frame(self.root, padding=5)
        info_frame.pack(fill=tk.X)
        self.info_label = ttk.Label(info_frame, text="等待加载图片...")
        self.info_label.pack(side=tk.LEFT)
    
    def _update_status(self, text, color="green"):
        """更新状态"""
        self.status_label.config(text=text, foreground=color)
        self.root.update()
    
    def _take_screenshot(self):
        """执行截图"""
        url = self.url_entry.get().strip()
        if not url or not url.startswith("http"):
            messagebox.showerror("错误", "请输入有效的URL")
            return
        
        self._update_status("正在截图...", "orange")
        
        def do_screenshot():
            try:
                output_path = "jd_screenshot.png"
                take_jd_screenshot(url, output_path)
                self.root.after(0, lambda: self._load_image(output_path))
                self.root.after(0, lambda: self._update_status("截图完成", "green"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("截图失败", str(e)))
                self.root.after(0, lambda: self._update_status("截图失败", "red"))
        
        # 在后台线程执行
        thread = threading.Thread(target=do_screenshot)
        thread.daemon = True
        thread.start()
    
    def _open_image(self):
        """打开本地图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self._load_image(file_path)
    
    def _load_image(self, path):
        """加载图片到画布"""
        try:
            self.image_path = path
            self.original_image = Image.open(path)
            self.current_image = self.original_image.copy()
            self.selections = []
            self._display_image()
            self.info_label.config(text=f"图片: {path} | 尺寸: {self.original_image.width}x{self.original_image.height}")
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")
    
    def _display_image(self):
        """显示图片"""
        if self.current_image is None:
            return
        
        # 计算缩放比例（适应画布大小，但不超过原图）
        canvas_width = self.canvas.winfo_width() or 1200
        canvas_height = self.canvas.winfo_height() or 700
        
        img_width, img_height = self.current_image.size
        
        # 计算适合的缩放
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        self.scale = min(scale_w, scale_h, 1.0)  # 不放大，只缩小
        
        # 创建显示用的图片
        display_width = int(img_width * self.scale)
        display_height = int(img_height * self.scale)
        
        display_img = self.current_image.copy()
        if self.scale < 1.0:
            display_img = display_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        self.photo_image = ImageTk.PhotoImage(display_img)
        
        # 清空画布并显示
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.canvas.config(scrollregion=(0, 0, display_width, display_height))
    
    def _on_mouse_down(self, event):
        """鼠标按下"""
        if self.current_image is None:
            return
        
        # 获取画布坐标
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # 创建选框
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
        """鼠标释放 - 弹出编辑对话框"""
        if self.current_image is None or self.rect_id is None:
            return
        
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # 计算选区（转换回原图坐标）
        x1 = int(min(self.start_x, end_x) / self.scale)
        y1 = int(min(self.start_y, end_y) / self.scale)
        x2 = int(max(self.start_x, end_x) / self.scale)
        y2 = int(max(self.start_y, end_y) / self.scale)
        
        width = x2 - x1
        height = y2 - y1
        
        # 忽略太小的选区
        if width < 10 or height < 10:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            return
        
        # 弹出输入框
        new_text = simpledialog.askstring(
            "输入新文字",
            f"选区: ({x1}, {y1}) - {width}x{height}\n请输入要显示的新文字:",
            parent=self.root
        )
        
        if new_text:
            # 执行修改
            self.current_image = edit_region(
                self.current_image,
                x1, y1, width, height,
                new_text,
                bg_color=self.bg_color_var.get() if self.bg_color_var.get() != "auto" else "white",
                text_color=self.color_var.get(),
                font_size=self.font_size_var.get()
            )
            self.selections.append((x1, y1, width, height, new_text))
            self._display_image()
            self._update_status(f"已修改 {len(self.selections)} 处", "blue")
        
        # 清除选框
        self.canvas.delete(self.rect_id)
        self.rect_id = None
    
    def _undo_all(self):
        """撤销所有修改"""
        if self.original_image is None:
            return
        
        if messagebox.askyesno("确认", "确定要撤销所有修改吗？"):
            self.current_image = self.original_image.copy()
            self.selections = []
            self._display_image()
            self._update_status("已撤销所有修改", "green")
    
    def _save_image(self):
        """保存图片"""
        if self.current_image is None:
            messagebox.showerror("错误", "没有可保存的图片")
            return
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")],
            initialfile="edited_screenshot.png"
        )
        
        if not file_path:
            return
        
        try:
            img_to_save = self.current_image.copy()
            
            # 添加水印
            if self.watermark_var.get():
                img_to_save = add_watermark(img_to_save, "仅供内部培训使用")
            
            save_image(img_to_save, file_path)
            self._update_status(f"已保存: {Path(file_path).name}", "green")
            messagebox.showinfo("成功", f"图片已保存到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))


def main():
    root = tk.Tk()
    app = ScreenshotEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()





