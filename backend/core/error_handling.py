from typing import Any, Dict, Optional
from fastapi import HTTPException
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """サービス固有のエラーの基底クラス"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)

class ValidationError(ServiceError):
    """バリデーションエラー"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(ServiceError):
    """認証エラー"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)

class AuthorizationError(ServiceError):
    """認可エラー"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)

class NotFoundError(ServiceError):
    """リソース未検出エラー"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class ConflictError(ServiceError):
    """競合エラー"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)

def handle_service_error(error: ServiceError) -> HTTPException:
    """ServiceErrorをHTTPExceptionに変換"""
    logger.error(f"Service error occurred: {error.message}", extra={
        "status_code": error.status_code,
        "details": error.details,
        "timestamp": error.timestamp.isoformat()
    })
    return HTTPException(
        status_code=error.status_code,
        detail={
            "message": error.message,
            "details": error.details,
            "timestamp": error.timestamp.isoformat()
        }
    ) 