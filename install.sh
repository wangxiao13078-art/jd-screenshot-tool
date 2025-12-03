#!/bin/bash
# 京东截图编辑工具 - 一键安装脚本
# 适用于 macOS / Linux

echo "================================"
echo "  京东截图编辑工具 - 安装程序"
echo "================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    echo "   macOS: brew install python3"
    echo "   Ubuntu: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python 版本: $PYTHON_VERSION"

# 进入脚本所在目录
cd "$(dirname "$0")"
echo "📁 工作目录: $(pwd)"

# 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo ""
echo "📥 安装依赖包..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 安装 Playwright 浏览器
echo ""
echo "🌐 下载 Chromium 浏览器（约 200MB）..."
playwright install chromium

echo ""
echo "================================"
echo "  ✅ 安装完成！"
echo "================================"
echo ""
echo "使用方法："
echo "  1. 运行启动脚本: ./start.sh"
echo "  2. 或手动启动:"
echo "     source venv/bin/activate"
echo "     python app.py"
echo ""
echo "  3. 打开浏览器访问: http://127.0.0.1:7860"
echo ""


