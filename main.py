"""
软件秘钥授权系统 - FastAPI 主应用
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database.models import (
    LicenseVerifyResponse, LicenseGenerateRequest, LicenseGenerateResponse,
    LicenseStatus, PlanType
)
from database.connection import db_manager
from utils.license_generator import generate_license_key
from utils.validators import validate_license_key_format

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="软件秘钥授权系统",
    description="支持多种授权类型的软件授权管理系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 授权类型对应的天数映射
PLAN_DAYS_MAPPING = {
    PlanType.TRIAL1: 1,
    PlanType.TRIAL3: 3,
    PlanType.DAYS30: 30,
    PlanType.DAYS180: 180,
    PlanType.DAYS365: 365,
    PlanType.LIFETIME: None  # 永久授权
}


@app.get("/", response_model=dict)
async def root():
    """根路径，返回API信息"""
    return {
        "message": "软件秘钥授权系统 API",
        "version": "1.0.0",
        "ui": "/static/index.html",
        "docs": "/docs",
        "endpoints": {
            "verify": "/verify/{license_key}",
            "generate": "/generate"
        }
    }


@app.get("/health", response_model=dict)
async def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        db_manager.execute_query("SELECT 1")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@app.get("/verify/{license_key}", response_model=LicenseVerifyResponse)
async def verify_license(license_key: str):
    """
    验证授权码
    
    Args:
        license_key: 授权码
        
    Returns:
        LicenseVerifyResponse: 验证结果
    """
    try:
        # 验证授权码格式
        if not validate_license_key_format(license_key):
            return LicenseVerifyResponse(
                status=LicenseStatus.NOT_FOUND,
                message="授权码格式无效"
            )
        
        # 查询数据库
        query = """
        SELECT id, license_key, user_email, plan_type, start_date, end_date, is_active
        FROM licenses 
        WHERE license_key = ?
        """
        
        results = db_manager.execute_query(query, (license_key,))
        
        if not results:
            logger.warning(f"License key not found: {license_key}")
            return LicenseVerifyResponse(
                status=LicenseStatus.NOT_FOUND,
                message="授权码不存在"
            )
        
        license_data = results[0]
        
        # 检查是否被禁用
        if not license_data['is_active']:
            logger.warning(f"License key disabled: {license_key}")
            return LicenseVerifyResponse(
                status=LicenseStatus.DISABLED,
                message="授权码已被禁用"
            )
        
        # 检查是否过期（永久授权除外）
        if license_data['plan_type'] != PlanType.LIFETIME and license_data['end_date']:
            from datetime import datetime
            end_date = datetime.fromisoformat(license_data['end_date'])
            if datetime.now() > end_date:
                logger.warning(f"License key expired: {license_key}")
                return LicenseVerifyResponse(
                    status=LicenseStatus.EXPIRED,
                    message="授权码已过期"
                )
        
        # 授权码有效
        logger.info(f"License key verified successfully: {license_key}")
        return LicenseVerifyResponse(
            status=LicenseStatus.VALID,
            plan_type=PlanType(license_data['plan_type']),
            end_date=datetime.fromisoformat(license_data['end_date']) if license_data['end_date'] else None,
            user_email=license_data['user_email'],
            message="授权码验证成功"
        )
        
    except Exception as e:
        logger.error(f"Error verifying license key {license_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@app.post("/generate", response_model=LicenseGenerateResponse)
async def generate_license(request: LicenseGenerateRequest):
    """
    生成新的授权码（管理端接口）
    
    Args:
        request: 生成请求参数
        
    Returns:
        LicenseGenerateResponse: 生成的授权码信息
    """
    try:
        # 生成唯一的授权码
        license_key = generate_license_key()
        
        # 计算结束时间
        end_date = None
        if request.plan_type != PlanType.LIFETIME:
            days = PLAN_DAYS_MAPPING[request.plan_type]
            end_date = datetime.now() + timedelta(days=days)
        
        # 插入数据库
        insert_query = """
        INSERT INTO licenses (id, license_key, user_email, plan_type, start_date, end_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        import uuid
        license_id = str(uuid.uuid4())
        
        db_manager.execute_insert(
            insert_query,
            (
                license_id,
                license_key,
                request.user_email,
                request.plan_type.value,
                datetime.now().isoformat(),
                end_date.isoformat() if end_date else None,
                True
            )
        )
        
        logger.info(f"Generated new license key: {license_key} for plan: {request.plan_type}")
        
        return LicenseGenerateResponse(
            license_key=license_key,
            plan_type=request.plan_type,
            end_date=end_date,
            user_email=request.user_email,
            message=f"成功生成{request.plan_type.value}授权码"
        )
        
    except Exception as e:
        logger.error(f"Error generating license key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成授权码失败"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误"}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
