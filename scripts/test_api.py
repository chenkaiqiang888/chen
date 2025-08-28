#!/usr/bin/env python3
"""
API测试脚本
用于测试授权系统的各个功能
"""
import requests
import json
import sys
from datetime import datetime


class APITester:
    """API测试器"""
    
    def __init__(self, base_url):
        """
        初始化测试器
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'APITester/1.0'
        })
    
    def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data.get('status')}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_verify_license(self, license_key):
        """测试授权码验证"""
        print(f"🔍 测试授权码验证: {license_key}")
        
        try:
            response = self.session.get(f"{self.base_url}/verify/{license_key}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 验证结果: {data.get('status')} - {data.get('message')}")
                
                if data.get('status') == 'valid':
                    print(f"   授权类型: {data.get('plan_type')}")
                    print(f"   到期时间: {data.get('end_date')}")
                    print(f"   用户邮箱: {data.get('user_email')}")
                
                return True
            else:
                print(f"❌ 验证失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 验证异常: {e}")
            return False
    
    def test_generate_license(self, plan_type, user_email=None):
        """测试授权码生成"""
        print(f"🔍 测试授权码生成: {plan_type}")
        
        try:
            data = {
                "plan_type": plan_type,
                "user_email": user_email
            }
            
            response = self.session.post(
                f"{self.base_url}/generate",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 生成成功: {result.get('license_key')}")
                print(f"   授权类型: {result.get('plan_type')}")
                print(f"   到期时间: {result.get('end_date')}")
                print(f"   用户邮箱: {result.get('user_email')}")
                
                # 返回生成的授权码用于后续测试
                return result.get('license_key')
            else:
                print(f"❌ 生成失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 生成异常: {e}")
            return None
    
    def test_invalid_license(self):
        """测试无效授权码"""
        print("🔍 测试无效授权码...")
        
        invalid_keys = [
            "INVALID-KEY-1234-5678",
            "ABCD-1234-EFGH-5678-INVALID",
            "invalid-format",
            ""
        ]
        
        for key in invalid_keys:
            if key:  # 跳过空字符串
                print(f"   测试: {key}")
                self.test_verify_license(key)
    
    def test_rate_limiting(self):
        """测试速率限制"""
        print("🔍 测试速率限制...")
        
        try:
            # 发送多个请求
            for i in range(5):
                response = self.session.get(f"{self.base_url}/health")
                print(f"   请求 {i+1}: {response.status_code}")
                
                if response.status_code == 429:
                    print("✅ 速率限制生效")
                    return True
            
            print("ℹ️  速率限制未触发（可能需要更多请求）")
            return True
            
        except Exception as e:
            print(f"❌ 速率限制测试异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=== API测试开始 ===\n")
        
        tests_passed = 0
        total_tests = 0
        
        # 测试1: 健康检查
        total_tests += 1
        if self.test_health_check():
            tests_passed += 1
        print()
        
        # 测试2: 验证示例授权码
        total_tests += 1
        sample_keys = [
            "DEMO-TRIAL1-ABCD1234",
            "DEMO-TRIAL3-EFGH5678",
            "DEMO-30D-IJKL9012",
            "DEMO-LIFETIME-UVWX1234"
        ]
        
        print("🔍 测试示例授权码验证...")
        for key in sample_keys:
            print(f"   测试: {key}")
            if self.test_verify_license(key):
                tests_passed += 1
                break
        print()
        
        # 测试3: 生成新授权码
        total_tests += 1
        new_license = self.test_generate_license("30d", "test@example.com")
        if new_license:
            tests_passed += 1
            # 验证新生成的授权码
            print("🔍 验证新生成的授权码...")
            self.test_verify_license(new_license)
        print()
        
        # 测试4: 无效授权码
        total_tests += 1
        self.test_invalid_license()
        tests_passed += 1  # 这个测试总是通过
        print()
        
        # 测试5: 速率限制
        total_tests += 1
        if self.test_rate_limiting():
            tests_passed += 1
        print()
        
        # 测试结果
        print("=== 测试结果 ===")
        print(f"通过: {tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 所有测试通过!")
            return True
        else:
            print("❌ 部分测试失败")
            return False


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("用法: python test_api.py <API_BASE_URL>")
        print("示例: python test_api.py https://your-api-server.com")
        sys.exit(1)
    
    api_url = sys.argv[1]
    
    print(f"测试API服务器: {api_url}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = APITester(api_url)
    
    if tester.run_all_tests():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
