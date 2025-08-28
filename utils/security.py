"""
安全工具模块
"""
import hashlib
import hmac
import time
import secrets
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """安全管理器"""
    
    def __init__(self, secret_key: str):
        """
        初始化安全管理器
        
        Args:
            secret_key: 密钥
        """
        self.secret_key = secret_key.encode('utf-8')
    
    def generate_hmac(self, data: str) -> str:
        """
        生成HMAC签名
        
        Args:
            data: 要签名的数据
            
        Returns:
            str: HMAC签名
        """
        return hmac.new(
            self.secret_key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_hmac(self, data: str, signature: str) -> bool:
        """
        验证HMAC签名
        
        Args:
            data: 原始数据
            signature: 签名
            
        Returns:
            bool: 签名是否有效
        """
        expected_signature = self.generate_hmac(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def generate_api_key(self) -> str:
        """
        生成API密钥
        
        Returns:
            str: API密钥
        """
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 原始密码
            
        Returns:
            str: 哈希后的密码
        """
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        验证密码
        
        Args:
            password: 原始密码
            password_hash: 哈希后的密码
            
        Returns:
            bool: 密码是否正确
        """
        try:
            salt, hash_value = password_hash.split(':')
            password_hash_check = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return hmac.compare_digest(hash_value, password_hash_check.hex())
        except ValueError:
            return False


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        初始化速率限制器
        
        Args:
            max_requests: 最大请求数
            window_seconds: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {ip: [timestamp1, timestamp2, ...]}
    
    def is_allowed(self, ip: str) -> bool:
        """
        检查IP是否允许请求
        
        Args:
            ip: IP地址
            
        Returns:
            bool: 是否允许
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # 清理过期的请求记录
        if ip in self.requests:
            self.requests[ip] = [
                timestamp for timestamp in self.requests[ip]
                if timestamp > window_start
            ]
        else:
            self.requests[ip] = []
        
        # 检查请求数量
        if len(self.requests[ip]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[ip].append(now)
        return True
    
    def get_remaining_requests(self, ip: str) -> int:
        """
        获取剩余请求数
        
        Args:
            ip: IP地址
            
        Returns:
            int: 剩余请求数
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        if ip in self.requests:
            valid_requests = [
                timestamp for timestamp in self.requests[ip]
                if timestamp > window_start
            ]
            return max(0, self.max_requests - len(valid_requests))
        
        return self.max_requests


class InputSanitizer:
    """输入清理器"""
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 255) -> str:
        """
        清理字符串输入
        
        Args:
            text: 输入文本
            max_length: 最大长度
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
        
        # 移除前后空格
        text = text.strip()
        
        # 限制长度
        if len(text) > max_length:
            text = text[:max_length]
        
        # 移除潜在的危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$', '\\', '/']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text
    
    @staticmethod
    def validate_license_key_format(license_key: str) -> bool:
        """
        验证授权码格式
        
        Args:
            license_key: 授权码
            
        Returns:
            bool: 格式是否正确
        """
        if not license_key or not isinstance(license_key, str):
            return False
        
        # 检查长度
        if len(license_key) != 19:  # XXXX-XXXX-XXXX-XXXX
            return False
        
        # 检查格式
        parts = license_key.split('-')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if len(part) != 4:
                return False
            # 检查是否只包含允许的字符
            if not all(c in "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" for c in part):
                return False
        
        return True


# 全局实例
security_manager = SecurityManager(os.getenv("SECRET_KEY", "default-secret-key"))
rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)
input_sanitizer = InputSanitizer()
