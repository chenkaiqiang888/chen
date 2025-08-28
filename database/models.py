"""
数据库模型定义
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


class PlanType(str, Enum):
    """授权类型枚举"""
    TRIAL1 = "trial1"      # 1天试用
    TRIAL3 = "trial3"      # 3天试用
    DAYS30 = "30d"         # 30天
    DAYS180 = "180d"       # 180天
    DAYS365 = "365d"       # 365天
    LIFETIME = "lifetime"  # 永久使用权


class LicenseStatus(str, Enum):
    """授权状态枚举"""
    VALID = "valid"
    EXPIRED = "expired"
    DISABLED = "disabled"
    NOT_FOUND = "not_found"


class LicenseBase(BaseModel):
    """授权码基础模型"""
    license_key: str
    user_email: Optional[EmailStr] = None
    plan_type: PlanType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class LicenseCreate(LicenseBase):
    """创建授权码模型"""
    pass


class LicenseUpdate(BaseModel):
    """更新授权码模型"""
    user_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class LicenseResponse(LicenseBase):
    """授权码响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LicenseVerifyRequest(BaseModel):
    """授权码验证请求模型"""
    license_key: str


class LicenseVerifyResponse(BaseModel):
    """授权码验证响应模型"""
    status: LicenseStatus
    plan_type: Optional[PlanType] = None
    end_date: Optional[datetime] = None
    user_email: Optional[str] = None
    message: Optional[str] = None


class LicenseGenerateRequest(BaseModel):
    """授权码生成请求模型"""
    plan_type: PlanType
    user_email: Optional[EmailStr] = None


class LicenseGenerateResponse(BaseModel):
    """授权码生成响应模型"""
    license_key: str
    plan_type: PlanType
    end_date: Optional[datetime] = None
    user_email: Optional[str] = None
    message: str
