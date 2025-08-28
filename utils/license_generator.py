"""
授权码生成工具
"""
import secrets
import string
from typing import Set


def generate_license_key() -> str:
    """
    生成唯一的授权码
    
    格式: XXXX-XXXX-XXXX-XXXX
    使用大写字母和数字，避免容易混淆的字符
    
    Returns:
        str: 生成的授权码
    """
    # 使用大写字母和数字，排除容易混淆的字符
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    
    # 生成4组4位字符
    segments = []
    for _ in range(4):
        segment = ''.join(secrets.choice(characters) for _ in range(4))
        segments.append(segment)
    
    return '-'.join(segments)


def generate_batch_license_keys(count: int) -> Set[str]:
    """
    批量生成唯一的授权码
    
    Args:
        count: 生成数量
        
    Returns:
        Set[str]: 生成的授权码集合
    """
    license_keys = set()
    
    while len(license_keys) < count:
        key = generate_license_key()
        license_keys.add(key)
    
    return license_keys


def validate_license_key_format(license_key: str) -> bool:
    """
    验证授权码格式是否正确
    
    Args:
        license_key: 待验证的授权码
        
    Returns:
        bool: 格式是否正确
    """
    if not license_key or not isinstance(license_key, str):
        return False
    
    # 检查格式: XXXX-XXXX-XXXX-XXXX
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


def get_license_key_entropy() -> int:
    """
    计算授权码的熵值（安全强度）
    
    Returns:
        int: 熵值（位数）
    """
    # 每个字符有32种可能（排除容易混淆的字符）
    # 总共16个字符
    import math
    return int(math.log2(32 ** 16))
