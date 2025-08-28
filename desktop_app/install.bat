@echo off
echo ========================================
echo 软件秘钥授权系统 - 桌面版安装程序
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)

echo.
echo 安装完成！
echo.
echo 启动方式:
echo 1. 双击 run.bat 启动程序
echo 2. 或在命令行运行: python main.py
echo.
pause

