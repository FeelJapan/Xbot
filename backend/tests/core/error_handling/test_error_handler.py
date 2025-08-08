import pytest
import asyncio
from core.error_handling.error_handler import (
    XbotError,
    APIError,
    ConfigError,
    ValidationError,
    handle_errors,
    validate_input
)

def test_error_classes():
    """エラークラスのテスト"""
    # 基本エラークラス
    error = XbotError("Test error", "TEST001")
    assert str(error) == "Test error"
    assert error.error_code == "TEST001"
    
    # APIエラー
    api_error = APIError("API error", "API001")
    assert isinstance(api_error, XbotError)
    assert str(api_error) == "API error"
    
    # 設定エラー
    config_error = ConfigError("Config error", "CONFIG001")
    assert isinstance(config_error, XbotError)
    assert str(config_error) == "Config error"
    
    # バリデーションエラー
    validation_error = ValidationError("Validation error", "VALID001")
    assert isinstance(validation_error, XbotError)
    assert str(validation_error) == "Validation error"

def test_handle_errors_sync():
    """同期関数のエラーハンドリングテスト"""
    @handle_errors(retry_count=2, retry_delay=0.1)
    def failing_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        failing_function()

def test_handle_errors_sync_with_fallback():
    """フォールバック付き同期関数のエラーハンドリングテスト"""
    def fallback_function():
        return "fallback result"
    
    @handle_errors(retry_count=2, retry_delay=0.1, fallback=fallback_function)
    def failing_function():
        raise ValueError("Test error")
    
    result = failing_function()
    assert result == "fallback result"

@pytest.mark.asyncio
async def test_handle_errors_async():
    """非同期関数のエラーハンドリングテスト"""
    @handle_errors(retry_count=2, retry_delay=0.1)
    async def failing_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await failing_function()

@pytest.mark.asyncio
async def test_handle_errors_async_with_fallback():
    """フォールバック付き非同期関数のエラーハンドリングテスト"""
    async def fallback_function():
        return "fallback result"
    
    @handle_errors(retry_count=2, retry_delay=0.1, fallback=fallback_function)
    async def failing_function():
        raise ValueError("Test error")
    
    result = await failing_function()
    assert result == "fallback result"

def test_handle_errors_success():
    """成功時のエラーハンドリングテスト"""
    @handle_errors()
    def successful_function():
        return "success"
    
    result = successful_function()
    assert result == "success"

@pytest.mark.asyncio
async def test_handle_errors_async_success():
    """非同期関数の成功時のエラーハンドリングテスト"""
    @handle_errors()
    async def successful_function():
        return "success"
    
    result = await successful_function()
    assert result == "success"

def test_validate_input():
    """入力バリデーションのテスト"""
    def is_positive(x):
        return x > 0
    
    @validate_input(is_positive, "Value must be positive")
    def test_function(x):
        return x * 2
    
    # 正常系
    assert test_function(5) == 10
    
    # 異常系
    with pytest.raises(ValidationError) as exc_info:
        test_function(-1)
    assert str(exc_info.value) == "Value must be positive"

def test_validate_input_with_multiple_args():
    """複数引数の入力バリデーションのテスト"""
    def validate_args(x, y):
        return x > 0 and y > 0
    
    @validate_input(validate_args, "Both values must be positive")
    def test_function(x, y):
        return x + y
    
    # 正常系
    assert test_function(5, 3) == 8
    
    # 異常系
    with pytest.raises(ValidationError) as exc_info:
        test_function(-1, 3)
    assert str(exc_info.value) == "Both values must be positive" 