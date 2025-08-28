"""
Python客户端示例 - 软件授权验证
"""
import requests
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any


class LicenseClient:
    """授权码验证客户端"""
    
    def __init__(self, api_base_url: str):
        """
        初始化客户端
        
        Args:
            api_base_url: API服务器基础URL
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LicenseClient/1.0'
        })
    
    def verify_license(self, license_key: str) -> Dict[str, Any]:
        """
        验证授权码
        
        Args:
            license_key: 授权码
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            url = f"{self.api_base_url}/verify/{license_key}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"API请求失败: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"网络请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"验证失败: {str(e)}"
            }
    
    def check_license_status(self, license_key: str) -> bool:
        """
        检查授权码状态（简化版本）
        
        Args:
            license_key: 授权码
            
        Returns:
            bool: 是否有效
        """
        result = self.verify_license(license_key)
        return result.get("status") == "valid"


def main():
    """主函数 - 演示客户端使用"""
    # 配置API服务器地址
    API_BASE_URL = "https://your-api-server.com"  # 替换为实际的API地址
    
    # 创建客户端
    client = LicenseClient(API_BASE_URL)
    
    print("=== 软件授权验证系统 ===")
    print("请输入您的授权码:")
    
    # 获取用户输入的授权码
    license_key = input().strip()
    
    if not license_key:
        print("错误: 授权码不能为空")
        sys.exit(1)
    
    print(f"\n正在验证授权码: {license_key}")
    print("请稍候...")
    
    # 验证授权码
    result = client.verify_license(license_key)
    
    # 显示结果
    print("\n=== 验证结果 ===")
    
    if result.get("status") == "valid":
        print("✅ 授权码验证成功!")
        print(f"授权类型: {result.get('plan_type', '未知')}")
        
        end_date = result.get('end_date')
        if end_date:
            print(f"到期时间: {end_date}")
        else:
            print("授权类型: 永久使用权")
        
        user_email = result.get('user_email')
        if user_email:
            print(f"绑定邮箱: {user_email}")
        
        print("\n软件启动成功! 欢迎使用!")
        
    elif result.get("status") == "expired":
        print("❌ 授权码已过期")
        print("请联系管理员续费或购买新的授权码")
        
    elif result.get("status") == "disabled":
        print("❌ 授权码已被禁用")
        print("请联系管理员了解详情")
        
    elif result.get("status") == "not_found":
        print("❌ 授权码不存在")
        print("请检查授权码是否正确")
        
    else:
        print("❌ 验证失败")
        print(f"错误信息: {result.get('message', '未知错误')}")
    
    # 根据验证结果决定是否退出
    if result.get("status") != "valid":
        print("\n软件无法启动，请解决授权问题后重试。")
        sys.exit(1)


if __name__ == "__main__":
    main()
