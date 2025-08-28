"""
错误处理工具
"""
import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    """自定义HTTP异常"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.additional_data = additional_data or {}


class LicenseSystemError(Exception):
    """授权系统基础异常"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseError(LicenseSystemError):
    """数据库错误"""
    pass


class ValidationError(LicenseSystemError):
    """验证错误"""
    pass


class SecurityError(LicenseSystemError):
    """安全错误"""
    pass


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    additional_data: Dict[str, Any] = None
) -> JSONResponse:
    """
    创建标准错误响应
    
    Args:
        status_code: HTTP状态码
        message: 错误消息
        error_code: 错误代码
        additional_data: 额外数据
        
    Returns:
        JSONResponse: 错误响应
    """
    error_data = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if error_code:
        error_data["error_code"] = error_code
    
    if additional_data:
        error_data.update(additional_data)
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        error_code=getattr(exc, 'error_code', None),
        additional_data=getattr(exc, 'additional_data', None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """验证异常处理器"""
    logger.warning(f"Validation Error: {exc.errors()}")
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="请求参数验证失败",
        error_code="VALIDATION_ERROR",
        additional_data={"validation_errors": exc.errors()}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(f"Unhandled Exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="服务器内部错误",
        error_code="INTERNAL_SERVER_ERROR"
    )


async def license_system_error_handler(request: Request, exc: LicenseSystemError) -> JSONResponse:
    """授权系统异常处理器"""
    logger.error(f"License System Error: {exc.message}")
    
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=exc.message,
        error_code=exc.error_code
    )


def handle_database_error(e: Exception, operation: str) -> None:
    """
    处理数据库错误
    
    Args:
        e: 异常对象
        operation: 操作描述
    """
    logger.error(f"Database error during {operation}: {str(e)}")
    raise DatabaseError(f"数据库操作失败: {operation}")


def handle_validation_error(message: str, field: str = None) -> None:
    """
    处理验证错误
    
    Args:
        message: 错误消息
        field: 字段名
    """
    if field:
        message = f"字段 '{field}' {message}"
    
    logger.warning(f"Validation error: {message}")
    raise ValidationError(message, "VALIDATION_ERROR")


def handle_security_error(message: str) -> None:
    """
    处理安全错误
    
    Args:
        message: 错误消息
    """
    logger.warning(f"Security error: {message}")
    raise SecurityError(message, "SECURITY_ERROR")


class ErrorCodes:
    """错误代码常量"""
    
    # 通用错误
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    
    # 授权相关错误
    LICENSE_NOT_FOUND = "LICENSE_NOT_FOUND"
    LICENSE_EXPIRED = "LICENSE_EXPIRED"
    LICENSE_DISABLED = "LICENSE_DISABLED"
    LICENSE_INVALID_FORMAT = "LICENSE_INVALID_FORMAT"
    
    # 数据库错误
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    
    # 网络错误
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # 权限错误
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
