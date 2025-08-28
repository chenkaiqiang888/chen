"""
安全中间件
"""
import time
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from utils.security import rate_limiter, input_sanitizer

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app, rate_limit_requests: int = 100, rate_limit_window: int = 3600):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求"""
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = self.get_client_ip(request)
        
        # 速率限制检查
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "请求过于频繁，请稍后再试",
                    "retry_after": self.rate_limit_window
                }
            )
        
        # 记录请求
        logger.info(f"Request: {request.method} {request.url} from {client_ip}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加安全头
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            return response
            
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "服务器内部错误"}
            )
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直接连接
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


class InputValidationMiddleware(BaseHTTPMiddleware):
    """输入验证中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求"""
        # 验证请求大小
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB限制
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "请求体过大"}
            )
        
        # 验证Content-Type
        content_type = request.headers.get("content-type", "")
        if request.method in ["POST", "PUT", "PATCH"]:
            if not content_type.startswith("application/json"):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={"detail": "不支持的媒体类型"}
                )
        
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求"""
        start_time = time.time()
        
        # 记录请求开始
        logger.info(f"Request started: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录请求完成
            logger.info(
                f"Request completed: {request.method} {request.url} "
                f"Status: {response.status_code} Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url} "
                f"Error: {str(e)} Time: {process_time:.3f}s"
            )
            raise
