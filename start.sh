#!/bin/bash
# 京东截图编辑工具 - 启动脚本

cd "$(dirname "$0")"

# 检查是否已安装
if [ ! -d "venv" ]; then
    echo "❌ 未安装，请先运行安装脚本:"
    echo "   ./install.sh"
    exit 1
fi

# 激活虚拟环境并启动
source venv/bin/activate
echo "🚀 启动京东截图编辑工具..."
echo "   访问地址: http://127.0.0.1:7860"
echo "   按 Ctrl+C 停止"
echo ""
python app.py


