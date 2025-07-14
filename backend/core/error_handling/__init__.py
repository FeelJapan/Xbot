"""
Error handling functionality for Xbot
"""

class ServiceError(Exception):
    """サービスの基本エラー"""
    pass

class ValidationError(Exception):
    """バリデーションエラー"""
    pass

class AuthenticationError(Exception):
    """認証エラー"""
    pass

class AuthorizationError(Exception):
    """認可エラー"""
    pass

class NotFoundError(Exception):
    """リソース未発見エラー"""
    pass

class ConflictError(Exception):
    """競合エラー"""
    pass

__all__ = [
    'ServiceError',
    'ValidationError',
    'AuthenticationError', 
    'AuthorizationError',
    'NotFoundError',
    'ConflictError',
] 