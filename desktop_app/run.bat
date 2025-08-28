@echo off
echo 正在启动软件秘钥授权系统...
python main.py
if errorlevel 1 (
    echo.
    echo 启动失败，请检查:
    echo 1. 是否已安装Python 3.8或更高版本
    echo 2. 是否已运行install.bat安装依赖包
    echo.
    pause
)

