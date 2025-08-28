#!/usr/bin/env python3
"""
快速启动脚本
用于本地开发和测试
"""
import os
import sys
import subprocess
from pathlib import Path


def check_requirements():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import psycopg2
        import dotenv
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("请复制 env.example 为 .env 并配置数据库连接")
        return False
    
    # 检查必要的环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 未设置 DATABASE_URL 环境变量")
        return False
    
    print("✅ 环境变量配置正确")
    return True


def setup_database():
    """设置数据库"""
    print("🔧 设置数据库...")
    
    try:
        # 运行数据库设置脚本
        result = subprocess.run([
            sys.executable, "scripts/setup_database.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 数据库设置完成")
            return True
        else:
            print(f"❌ 数据库设置失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 数据库设置异常: {e}")
        return False


def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    
    try:
        # 启动FastAPI服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")


def main():
    """主函数"""
    print("=== 软件秘钥授权系统 - 快速启动 ===\n")
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查环境变量
    if not check_env_file():
        sys.exit(1)
    
    # 询问是否设置数据库
    setup_db = input("\n是否设置数据库? (y/N): ").lower().strip()
    if setup_db in ['y', 'yes']:
        if not setup_database():
            sys.exit(1)
    
    # 启动服务器
    print("\n服务器将在 http://localhost:8000 启动")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务器\n")
    
    start_server()


if __name__ == "__main__":
    main()
