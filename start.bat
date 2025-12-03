@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "venv" (
    echo ❌ 未安装，请先运行 install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo 🚀 启动京东截图编辑工具...
echo    访问地址: http://127.0.0.1:7860
echo    关闭此窗口停止程序
echo.
python app.py


