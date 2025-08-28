"""
创建可执行文件的脚本
使用 PyInstaller 将Python程序打包为exe文件
"""

import os
import sys
import subprocess

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def create_exe():
    """创建exe文件"""
    print("正在创建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包为单个exe文件
        "--windowed",                   # 无控制台窗口
        "--name=软件秘钥授权系统",        # 设置exe文件名
        "--icon=icon.ico",              # 设置图标（如果存在）
        "--add-data=requirements.txt;.", # 包含依赖文件
        "main.py"                       # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.check_call(cmd)
        print("✅ 可执行文件创建成功")
        print("📁 输出文件位置: dist/软件秘钥授权系统.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建可执行文件失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 未找到PyInstaller，请先安装")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("软件秘钥授权系统 - 可执行文件创建工具")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not os.path.exists("main.py"):
        print("❌ 错误: 请在desktop_app目录下运行此脚本")
        return
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 创建exe文件
    if create_exe():
        print("\n🎉 打包完成！")
        print("📋 使用说明:")
        print("1. 在dist文件夹中找到'软件秘钥授权系统.exe'")
        print("2. 双击运行即可使用")
        print("3. 可以将exe文件复制到任何Windows电脑上运行")
    else:
        print("\n❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")

