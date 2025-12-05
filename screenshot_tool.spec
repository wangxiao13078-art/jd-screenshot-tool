# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# 收集Gradio的所有数据文件
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

gradio_datas = collect_data_files('gradio')
gradio_client_datas = collect_data_files('gradio_client')

# 收集Playwright（Windows环境）
playwright_datas = []
playwright_binaries = []
try:
    playwright_data = collect_all('playwright')
    playwright_datas += playwright_data[0]  # datas
    playwright_binaries += playwright_data[1]  # binaries
    
    # Windows下添加Playwright浏览器
    if sys.platform == 'win32':
        localappdata = os.environ.get('LOCALAPPDATA', '')
        playwright_path = os.path.join(localappdata, 'ms-playwright')
        if os.path.exists(playwright_path):
            playwright_datas.append((playwright_path, 'ms-playwright'))
except Exception as e:
    print(f"Warning: Could not collect Playwright data: {e}")

# 收集所有隐藏导入
hiddenimports = collect_submodules('gradio') + collect_submodules('gradio_client')
hiddenimports += collect_submodules('playwright')
hiddenimports += [
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
]

# 准备数据文件
all_datas = gradio_datas + gradio_client_datas + playwright_datas
if os.path.exists('fonts'):
    all_datas.append(('fonts', 'fonts'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=playwright_binaries,
    datas=all_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='京东截图编辑工具-完整版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加icon='icon.ico'
)

