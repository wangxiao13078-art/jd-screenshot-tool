#!/bin/bash
# 快速启动脚本

cd "$(dirname "$0")"

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 运行主程序
python main.py





