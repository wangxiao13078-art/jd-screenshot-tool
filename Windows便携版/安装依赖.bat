@echo off
chcp 65001 >nul
echo 正在安装依赖包...
python\python.exe -m pip install Pillow -q
echo.
echo ✓ 依赖安装完成！
echo.
echo 现在可以双击 启动.bat 运行程序了
pause

