#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 生成便携版可执行文件
"""

import subprocess
import sys
import platform

def build():
    system = platform.system()
    
    print("=" * 50)
    print("  京东截图编辑工具 - 打包程序")
    print("=" * 50)
    print(f"系统: {system}")
    print()
    
    # PyInstaller 参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 打包成单个文件
        "--windowed",          # 不显示控制台窗口
        "--name", "京东截图编辑工具",
        "--clean",             # 清理临时文件
    ]
    
    # macOS 特定选项
    if system == "Darwin":
        cmd.extend(["--osx-bundle-identifier", "com.jd.screenshot.editor"])
    
    # 添加主程序
    cmd.append("app_portable.py")
    
    print("正在打包...")
    print(f"命令: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print()
        print("=" * 50)
        print("  ✅ 打包完成！")
        print("=" * 50)
        print()
        if system == "Darwin":
            print("可执行文件位置: dist/京东截图编辑工具.app")
        elif system == "Windows":
            print("可执行文件位置: dist/京东截图编辑工具.exe")
        else:
            print("可执行文件位置: dist/京东截图编辑工具")
        print()
        print("将 dist 文件夹拷贝到U盘即可在其他电脑使用")
        print("（目标电脑需要是相同的操作系统）")
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()

