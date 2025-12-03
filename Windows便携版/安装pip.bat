@echo off
chcp 65001 >nul
echo 正在安装 pip...
python\python.exe get-pip.py
echo.
echo 修改配置以支持第三方库...
echo import site >> python\python311._pth
echo.
echo pip 安装完成！
pause

