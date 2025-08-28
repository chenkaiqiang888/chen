"""
验证工具
"""
import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError


def validate_license_key_format(license_key: str) -> bool:
    """
    验证授权码格式
    
    Args:
        license_key: 授权码
        
    Returns:
        bool: 是否有效
    """
    if not license_key or not isinstance(license_key, str):
        return False
    
    # 格式: XXXX-XXXX-XXXX-XXXX
    pattern = r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return bool(re.match(pattern, license_key))


def validate_email_format(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
    """
    if not email or not isinstance(email, str):
        return False
    
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def sanitize_input(text: str, max_length: int = 255) -> str:
    """
    清理用户输入
    
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
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text


def validate_plan_type(plan_type: str) -> bool:
    """
    验证授权类型
    
    Args:
        plan_type: 授权类型
        
    Returns:
        bool: 是否有效
    """
    valid_plans = ['trial1', 'trial3', '30d', '180d', '365d', 'lifetime']
    return plan_type in valid_plans
