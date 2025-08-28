@echo off
echo ========================================
echo Render部署脚本
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "main.py" (
    echo 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查Git状态
git status --porcelain >nul 2>&1
if %errorlevel% equ 0 (
    echo 警告: 有未提交的更改
    set /p continue="是否继续部署? (y/N): "
    if /i not "%continue%"=="y" (
        echo 部署已取消
        pause
        exit /b 1
    )
)

REM 推送到GitHub
echo 正在推送到GitHub...
git add .
git commit -m "Deploy to Render - %date% %time%"
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo 代码已推送到GitHub
    echo.
    echo 接下来请手动完成以下步骤：
    echo.
    echo 1. 访问 https://render.com
    echo 2. 登录您的账号
    echo 3. 创建PostgreSQL数据库服务
    echo 4. 创建Web服务并连接GitHub仓库
    echo 5. 设置环境变量（特别是DATABASE_URL）
    echo 6. 等待部署完成
    echo.
    echo 详细步骤请参考: deploy/RENDER_DEPLOYMENT.md
    echo.
    echo 部署脚本执行完成！
) else (
    echo 错误: 推送到GitHub失败
    echo 请检查Git配置和网络连接
)

echo.
pause
