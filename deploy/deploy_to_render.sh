#!/bin/bash

# Render部署脚本
echo "🚀 开始部署到Render..."

# 检查是否在正确的目录
if [ ! -f "main.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告: 有未提交的更改"
    read -p "是否继续部署? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 1
    fi
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git add .
git commit -m "Deploy to Render - $(date)"
git push origin main

echo "✅ 代码已推送到GitHub"
echo ""
echo "📋 接下来请手动完成以下步骤："
echo ""
echo "1. 访问 https://render.com"
echo "2. 登录您的账号"
echo "3. 创建PostgreSQL数据库服务"
echo "4. 创建Web服务并连接GitHub仓库"
echo "5. 设置环境变量（特别是DATABASE_URL）"
echo "6. 等待部署完成"
echo ""
echo "📖 详细步骤请参考: deploy/RENDER_DEPLOYMENT.md"
echo ""
echo "🎉 部署脚本执行完成！"
