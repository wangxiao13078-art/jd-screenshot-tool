@echo off
chcp 65001 >nul
echo ================================
echo   京东截图编辑工具 - 安装程序
echo ================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 进入脚本目录
cd /d "%~dp0"
echo 📁 工作目录: %cd%

REM 创建虚拟环境
echo.
echo 📦 创建虚拟环境...
python -m venv venv

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo 📥 安装依赖包...
pip install --upgrade pip -q
pip install -r requirements.txt -q

REM 安装 Playwright 浏览器
echo.
echo 🌐 下载 Chromium 浏览器（约 200MB）...
playwright install chromium

echo.
echo ================================
echo   ✅ 安装完成！
echo ================================
echo.
echo 使用方法：
echo   1. 双击 start.bat 启动
echo   2. 打开浏览器访问: http://127.0.0.1:7860
echo.
pause


